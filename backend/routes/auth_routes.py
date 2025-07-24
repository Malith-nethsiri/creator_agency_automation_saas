from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService
from schemas.user import UserCreate, UserOut
from schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, UserProfile
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
from core.utils import create_response
from core.config import settings

router = APIRouter()

@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    user_service = UserService(db)

    try:
        user = user_service.create_user(user_data, background_tasks)

        return create_response(
            success=True,
            message="User registered successfully. Welcome email sent!",
            data={
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user and return JWT tokens"""
    user_service = UserService(db)

    user = user_service.authenticate_user(login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/login/form", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login using OAuth2 form (for Swagger UI)"""
    user_service = UserService(db)

    user = user_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except ValueError:
        raise credentials_exception

    # Verify user still exists
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    if not user:
        raise credentials_exception

    # Create new tokens
    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user = Depends(get_current_user)):
    """Get user profile information"""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role.value
    )

@router.post("/logout", response_model=dict)
async def logout():
    """Logout user (client should discard tokens)"""
    return create_response(
        success=True,
        message="Successfully logged out. Please discard your tokens."
    )

@router.get("/verify-token", response_model=dict)
async def verify_token(current_user = Depends(get_current_user)):
    """Verify if current token is valid"""
    return create_response(
        success=True,
        message="Token is valid",
        data={
            "user_id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value
        }
    )
