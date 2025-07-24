from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from services.content_service import ContentService
from schemas.content import ContentCreate, ContentOut, ContentOutWithCreator
from schemas.base import PaginatedResponse
from core.security import get_current_user, get_admin_user, require_roles
from core.utils import create_response
from models.user import UserRole

router = APIRouter()

@router.post("/", response_model=ContentOut, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["creator", "admin"]))
):
    """Create new content (Creator/Admin only)"""
    content_service = ContentService(db)

    try:
        content = content_service.create_content(content_data, current_user.id)
        return content
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )

@router.get("/my-content", response_model=dict)
async def get_my_content(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["creator", "admin"]))
):
    """Get current user's content"""
    content_service = ContentService(db)
    result = content_service.get_user_content(current_user.id, page, per_page)

    return create_response(
        success=True,
        message="Content retrieved successfully",
        data=result
    )

@router.get("/", response_model=dict)
async def get_all_content(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all content (Admin only)"""
    content_service = ContentService(db)
    result = content_service.get_all_content(page, per_page)

    return create_response(
        success=True,
        message="All content retrieved successfully",
        data=result
    )

@router.get("/{content_id}", response_model=ContentOutWithCreator)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific content by ID"""
    content_service = ContentService(db)
    content = content_service.get_content_with_creator(content_id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Check if user can access this content
    if (current_user.role != UserRole.ADMIN and
        content.creator_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this content"
        )

    return content

@router.delete("/{content_id}", response_model=dict)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete content"""
    content_service = ContentService(db)

    try:
        deleted_content = content_service.delete_content(
            content_id, current_user.id, current_user.role
        )

        return create_response(
            success=True,
            message="Content deleted successfully",
            data={"deleted_content_id": deleted_content.id}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content"
        )
