from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.relations import UserWithRelations
from services.user_service import UserService
from routes.auth import get_current_user
from core.utils import create_response

router = APIRouter()

@router.get("/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=dict)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_data)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return create_response(True, "Profile updated successfully")
