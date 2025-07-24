from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.content import Content
from models.user import UserRole
from schemas.content import ContentCreate
from services.base import BaseService

class ContentService(BaseService[Content, ContentCreate, None]):
    def __init__(self, db: Session):
        super().__init__(Content, db)

    def create_content(self, content_data: ContentCreate, creator_id: int) -> Content:
        """Create new content for a creator"""
        # Ensure the creator_id matches the authenticated user
        if content_data.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create content for another user"
            )

        db_content = Content(
            title=content_data.title,
            file_url=content_data.file_url,
            creator_id=creator_id
        )

        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)

        return db_content

    def get_user_content(self, creator_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all content by a specific creator"""
        query = self.db.query(Content).filter(Content.creator_id == creator_id)
        return self.paginate_query(query, page, per_page)

    def get_all_content(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all content (admin only)"""
        query = self.db.query(Content)
        return self.paginate_query(query, page, per_page)

    def get_content_with_creator(self, content_id: int) -> Optional[Content]:
        """Get content with creator information"""
        return self.db.query(Content).filter(Content.id == content_id).first()

    def delete_content(self, content_id: int, user_id: int, user_role: UserRole) -> Content:
        """Delete content (creator can delete own, admin can delete any)"""
        content = self.get_or_404(content_id)

        # Check permissions
        if user_role != UserRole.ADMIN and content.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this content"
            )

        self.db.delete(content)
        self.db.commit()
        return content

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
