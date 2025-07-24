from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.subscription import Subscription, SubscriptionStatus
from models.subscription_plan import SubscriptionPlan
from models.user import UserRole
from schemas.subscription import SubscriptionCreate
from schemas.subscription_plan import SubscriptionPlanCreate
from services.base import BaseService

class SubscriptionPlanService(BaseService[SubscriptionPlan, SubscriptionPlanCreate, None]):
    def __init__(self, db: Session):
        super().__init__(SubscriptionPlan, db)

    def get_all_plans(self) -> List[SubscriptionPlan]:
        """Get all available subscription plans"""
        return self.db.query(SubscriptionPlan).all()

    def create_plan(self, plan_data: SubscriptionPlanCreate) -> SubscriptionPlan:
        """Create new subscription plan (admin only)"""
        db_plan = SubscriptionPlan(
            name=plan_data.name,
            price=plan_data.price,
            features=plan_data.features
        )

        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)

        return db_plan

class SubscriptionService(BaseService[Subscription, SubscriptionCreate, None]):
    def __init__(self, db: Session):
        super().__init__(Subscription, db)

    def create_subscription(self, subscription_data: SubscriptionCreate, user_id: int) -> Subscription:
        """Create new subscription for a user"""
        # Ensure user_id matches authenticated user
        if subscription_data.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create subscription for another user"
            )

        # Check if plan exists
        plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription_data.plan_id
        ).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )

        # Check if user already has an active subscription
        existing_subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()

        if existing_subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription"
            )

        db_subscription = Subscription(
            user_id=user_id,
            plan_id=subscription_data.plan_id,
            status=subscription_data.status
        )

        self.db.add(db_subscription)
        self.db.commit()
        self.db.refresh(db_subscription)

        return db_subscription

    def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        """Get all subscriptions for a user"""
        return self.db.query(Subscription).filter(Subscription.user_id == user_id).all()

    def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get user's active subscription"""
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()

    def cancel_subscription(self, subscription_id: int, user_id: int, user_role: UserRole) -> Subscription:
        """Cancel a subscription"""
        subscription = self.get_or_404(subscription_id)

        # Check permissions
        if user_role != UserRole.ADMIN and subscription.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this subscription"
            )

        if subscription.status == SubscriptionStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already canceled"
            )

        subscription.status = SubscriptionStatus.CANCELED
        self.db.commit()
        self.db.refresh(subscription)

        return subscription

    def get_all_subscriptions(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all subscriptions (admin only)"""
        query = self.db.query(Subscription)
        return self.paginate_query(query, page, per_page)

    def paginate_query(self, query, page: int, per_page: int) -> Dict[str, Any]:
        """Paginate query results"""
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if total > 0 else 0
        }
