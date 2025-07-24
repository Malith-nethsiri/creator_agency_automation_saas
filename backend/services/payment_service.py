import stripe
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.config import settings
from models.subscription import Subscription, SubscriptionStatus
from models.subscription_plan import SubscriptionPlan
from models.user import User
from services.subscription_service import SubscriptionService
from services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)

    def create_checkout_session(
        self,
        plan_id: int,
        user_id: int,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create Stripe checkout session for subscription plan"""

        # Get subscription plan
        plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == plan_id
        ).first()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )

        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if user already has an active subscription
        existing_subscription = self.subscription_service.get_active_subscription(user_id)
        if existing_subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription"
            )

        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan.name,
                            'description': plan.features or f"Access to {plan.name} features",
                        },
                        'unit_amount': int(plan.price * 100),  # Convert to cents
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url or settings.STRIPE_SUCCESS_URL,
                cancel_url=cancel_url or settings.STRIPE_CANCEL_URL,
                client_reference_id=str(user_id),
                metadata={
                    'user_id': str(user_id),
                    'plan_id': str(plan_id),
                },
                customer_email=user.email,
            )

            return {
                'checkout_session_id': checkout_session.id,
                'checkout_url': checkout_session.url,
                'plan_name': plan.name,
                'plan_price': float(plan.price)
            }

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    def handle_checkout_completed(self, session: Dict[str, Any]) -> None:
        """Handle successful checkout completion"""
        try:
            user_id = int(session['metadata']['user_id'])
            plan_id = int(session['metadata']['plan_id'])
            stripe_subscription_id = session['subscription']

            # Get user and plan info
            user = self.db.query(User).filter(User.id == user_id).first()
            plan = self.db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()

            # Create subscription in database
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.ACTIVE,
                stripe_subscription_id=stripe_subscription_id
            )

            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)

            # Send subscription success email
            if user and plan:
                try:
                    email_service.send_subscription_success_email(
                        user_email=user.email,
                        user_name=user.email.split('@')[0],  # Use email prefix as name
                        plan_name=plan.name,
                        plan_price=float(plan.price)
                    )
                except Exception as e:
                    logger.error(f"Failed to send subscription success email: {str(e)}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error handling checkout completion: {str(e)}")
            raise e

    def handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> None:
        """Handle subscription status updates from Stripe"""
        try:
            stripe_subscription_id = subscription_data['id']
            stripe_status = subscription_data['status']

            # Find subscription in database
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_subscription_id
            ).first()

            if not subscription:
                return  # Subscription not found in our database

            # Map Stripe status to our status
            if stripe_status == 'active':
                subscription.status = SubscriptionStatus.ACTIVE
            elif stripe_status in ['canceled', 'unpaid', 'past_due']:
                subscription.status = SubscriptionStatus.CANCELED

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e

    def handle_subscription_deleted(self, subscription_data: Dict[str, Any]) -> None:
        """Handle subscription cancellation from Stripe"""
        try:
            stripe_subscription_id = subscription_data['id']

            # Find and cancel subscription in database
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_subscription_id
            ).first()

            if subscription:
                subscription.status = SubscriptionStatus.CANCELED
                self.db.commit()

                # Send cancellation email
                user = self.db.query(User).filter(User.id == subscription.user_id).first()
                plan = self.db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()

                if user and plan:
                    try:
                        email_service.send_subscription_cancellation_email(
                            user_email=user.email,
                            user_name=user.email.split('@')[0],  # Use email prefix as name
                            plan_name=plan.name
                        )
                    except Exception as e:
                        logger.error(f"Failed to send cancellation email: {str(e)}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error handling subscription deletion: {str(e)}")
            raise e

    def cancel_subscription(self, subscription_id: int, user_id: int) -> Dict[str, Any]:
        """Cancel subscription in Stripe and update database"""
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == user_id
        ).first()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )

        if subscription.status == SubscriptionStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already canceled"
            )

        try:
            # Cancel in Stripe
            if hasattr(subscription, 'stripe_subscription_id') and subscription.stripe_subscription_id:
                stripe.Subscription.delete(subscription.stripe_subscription_id)

            # Update database
            subscription.status = SubscriptionStatus.CANCELED
            self.db.commit()

            # Send cancellation email
            user = self.db.query(User).filter(User.id == user_id).first()
            plan = self.db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()

            if user and plan:
                try:
                    email_service.send_subscription_cancellation_email(
                        user_email=user.email,
                        user_name=user.email.split('@')[0],
                        plan_name=plan.name
                    )
                except Exception as e:
                    logger.error(f"Failed to send cancellation email: {str(e)}")

            return {"message": "Subscription canceled successfully"}

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    def get_subscription_details(self, stripe_subscription_id: str) -> Dict[str, Any]:
        """Get subscription details from Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'plan_name': subscription['items']['data'][0]['price']['product']['name']
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
