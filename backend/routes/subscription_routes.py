from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from services.subscription_service import SubscriptionService, SubscriptionPlanService
from schemas.subscription import SubscriptionCreate, SubscriptionOut, SubscriptionOutWithRelations
from schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanOut
from core.security import get_current_user, get_admin_user, require_roles
from core.utils import create_response
from models.user import UserRole

router = APIRouter()

# Subscription Plan endpoints
@router.get("/plans", response_model=List[SubscriptionPlanOut])
async def get_subscription_plans(db: Session = Depends(get_db)):
    """Get all available subscription plans (public)"""
    plan_service = SubscriptionPlanService(db)
    return plan_service.get_all_plans()

@router.post("/plans", response_model=SubscriptionPlanOut, status_code=status.HTTP_201_CREATED)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create new subscription plan (Admin only)"""
    plan_service = SubscriptionPlanService(db)

    try:
        plan = plan_service.create_plan(plan_data)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription plan"
        )

@router.get("/plans/{plan_id}", response_model=SubscriptionPlanOut)
async def get_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """Get specific subscription plan"""
    plan_service = SubscriptionPlanService(db)
    plan = plan_service.get_or_404(plan_id)
    return plan

@router.delete("/plans/{plan_id}", response_model=dict)
async def delete_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Delete subscription plan (Admin only)"""
    plan_service = SubscriptionPlanService(db)

    try:
        deleted_plan = plan_service.delete(id=plan_id)
        return create_response(
            success=True,
            message="Subscription plan deleted successfully",
            data={"deleted_plan_id": deleted_plan.id}
        )
    except HTTPException as e:
        raise e

# Subscription endpoints
@router.post("/", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
async def subscribe_to_plan(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Subscribe to a plan"""
    subscription_service = SubscriptionService(db)

    try:
        subscription = subscription_service.create_subscription(
            subscription_data, current_user.id
        )
        return subscription
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )

@router.get("/my-subscriptions", response_model=List[SubscriptionOutWithRelations])
async def get_my_subscriptions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's subscriptions"""
    subscription_service = SubscriptionService(db)
    subscriptions = subscription_service.get_user_subscriptions(current_user.id)
    return subscriptions

@router.get("/my-active-subscription", response_model=SubscriptionOutWithRelations)
async def get_my_active_subscription(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's active subscription"""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_active_subscription(current_user.id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    return subscription

@router.patch("/{subscription_id}/cancel", response_model=SubscriptionOut)
async def cancel_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel a subscription"""
    subscription_service = SubscriptionService(db)

    try:
        subscription = subscription_service.cancel_subscription(
            subscription_id, current_user.id, current_user.role
        )
        return subscription
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.get("/", response_model=dict)
async def get_all_subscriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all subscriptions (Admin only)"""
    subscription_service = SubscriptionService(db)
    result = subscription_service.get_all_subscriptions(page, per_page)

    return create_response(
        success=True,
        message="All subscriptions retrieved successfully",
        data=result
    )

@router.get("/{subscription_id}", response_model=SubscriptionOutWithRelations)
async def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific subscription"""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_or_404(subscription_id)

    # Check if user can access this subscription
    if (current_user.role != UserRole.ADMIN and
        subscription.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this subscription"
        )

    return subscription
