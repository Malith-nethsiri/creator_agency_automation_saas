import stripe
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from services.payment_service import PaymentService
from schemas.base import BaseSchema
from core.security import get_current_user
from core.utils import create_response
from core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class CheckoutSessionRequest(BaseSchema):
    plan_id: int
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class CancelSubscriptionRequest(BaseSchema):
    subscription_id: int

@router.post("/create-checkout-session", response_model=dict)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription plan"""
    payment_service = PaymentService(db)

    try:
        session_data = payment_service.create_checkout_session(
            plan_id=request.plan_id,
            user_id=current_user.id,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )

        return create_response(
            success=True,
            message="Checkout session created successfully",
            data=session_data
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )

@router.post("/cancel-subscription", response_model=dict)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel user's subscription"""
    payment_service = PaymentService(db)

    try:
        result = payment_service.cancel_subscription(
            subscription_id=request.subscription_id,
            user_id=current_user.id
        )

        return create_response(
            success=True,
            message="Subscription canceled successfully",
            data=result
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    payment_service = PaymentService(db)

    try:
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            logger.info(f"Checkout session completed: {session['id']}")
            payment_service.handle_checkout_completed(session)

        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            logger.info(f"Subscription updated: {subscription['id']}")
            payment_service.handle_subscription_updated(subscription)

        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            logger.info(f"Subscription deleted: {subscription['id']}")
            payment_service.handle_subscription_deleted(subscription)

        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            subscription_id = invoice['subscription']
            logger.warning(f"Payment failed for subscription: {subscription_id}")
            # Handle failed payment - could send notification email

        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return {"received": True}

    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

@router.get("/subscription-status/{subscription_id}")
async def get_subscription_status(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get subscription status from Stripe"""
    payment_service = PaymentService(db)

    try:
        subscription_details = payment_service.get_subscription_details(subscription_id)

        return create_response(
            success=True,
            message="Subscription details retrieved successfully",
            data=subscription_details
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting subscription status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status"
        )

@router.get("/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return create_response(
        success=True,
        message="Stripe configuration retrieved",
        data={
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY
        }
    )
