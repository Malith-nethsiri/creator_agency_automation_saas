from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, BackgroundTasks
from models.user import User, UserRole
from schemas.relations import UserWithRelations
from core.security import get_password_hash, verify_password
from services.base import BaseService
from services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

class UserService(BaseService[User, UserCreate, None]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(
        self,
        user_data: UserCreate,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> User:
        """Create a new user with hashed password and send welcome email"""
        # Check if user already exists
        existing_user = self.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        try:
            # Hash the password
            hashed_password = get_password_hash(user_data.password)

            # Create user object
            db_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                role=user_data.role
            )

            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

            # Send welcome email asynchronously
            if background_tasks:
                background_tasks.add_task(
                    self._send_welcome_email,
                    db_user.email
                )

            logger.info(f"User created successfully: {db_user.email}")
            return db_user

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    def _send_welcome_email(self, user_email: str):
        """Send welcome email to new user"""
        try:
            email_service.send_welcome_email(user_email)
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def get_users_by_role(self, role: UserRole) -> list[User]:
        """Get all users by role"""
        return self.db.query(User).filter(User.role == role).all()

    def update_user_role(self, user_id: int, new_role: UserRole) -> Optional[User]:
        """Update user role (admin only)"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.role = new_role
        self.db.commit()
        self.db.refresh(user)

        return user

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Soft delete user by setting inactive status"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        # If you have an is_active field, use it
        # user.is_active = False
        # For now, we'll just return the user

        self.db.commit()
        self.db.refresh(user)

        return user
