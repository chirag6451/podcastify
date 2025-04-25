"""
Purpose and Objective: 
This module provides API endpoints for user management including registration, 
authentication, profile management, and user settings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import List, Optional

from ..db import get_db
from ..models.user import User, UserSettings, BusinessInformation, PasswordReset
from ..schemas.user import (
    UserCreate, UserResponse, UserLogin, UserProfileUpdate,
    BusinessInformationCreate, BusinessInformationResponse,
    UserSettingsUpdate, UserSettingsResponse,
    Token, ChangePassword, PasswordResetRequest, PasswordReset as PasswordResetSchema
)
from ..auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password
    - **name**: User's full name
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create default user settings
        user_settings = UserSettings(
            user_id=new_user.id,
            autopilot_mode=False,
            default_language="en",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user_settings)
        db.commit()
        
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again."
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Get an access token for authentication.
    
    - **username**: User's email address
    - **password**: User's password
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get an access token.
    
    - **email**: User's email address
    - **password**: User's password
    """
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get the current authenticated user's profile.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the current user's profile.
    
    - **name**: Optional new name
    - **profile_picture**: Optional new profile picture URL
    """
    # Update user fields if provided
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.profile_picture is not None:
        current_user.profile_picture = user_update.profile_picture
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change the current user's password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password to set
    """
    # Verify current password
    if not authenticate_user(db, current_user.email, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current user's settings.
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User settings not found"
        )
    
    return settings

@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the current user's settings.
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        # Create settings if they don't exist
        settings = UserSettings(
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )
        db.add(settings)
    
    # Update settings fields if provided
    for key, value in settings_update.dict(exclude_unset=True).items():
        setattr(settings, key, value)
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    return settings

@router.post("/business", response_model=BusinessInformationResponse, status_code=status.HTTP_201_CREATED)
async def create_business_information(
    business_data: BusinessInformationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create or update business information for the current user.
    """
    # Check if business information already exists
    business_info = db.query(BusinessInformation).filter(
        BusinessInformation.user_id == current_user.id
    ).first()
    
    if business_info:
        # Update existing business information
        for key, value in business_data.dict().items():
            setattr(business_info, key, value)
        business_info.updated_at = datetime.utcnow()
    else:
        # Create new business information
        business_info = BusinessInformation(
            user_id=current_user.id,
            **business_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(business_info)
    
    db.commit()
    db.refresh(business_info)
    
    return business_info

@router.get("/business", response_model=BusinessInformationResponse)
async def get_business_information(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get business information for the current user.
    """
    business_info = db.query(BusinessInformation).filter(
        BusinessInformation.user_id == current_user.id
    ).first()
    
    if not business_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business information not found"
        )
    
    return business_info

# Password reset endpoints
@router.post("/reset-password/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset.
    
    - **email**: Email address for the account to reset
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        # Return success even if user doesn't exist to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate a reset token (in a real app, this would be a secure random token)
    import uuid
    reset_token = str(uuid.uuid4())
    
    # Store the reset token
    password_reset = PasswordReset(
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        created_at=datetime.utcnow()
    )
    db.add(password_reset)
    db.commit()
    
    # In a real app, send an email with the reset link
    # For now, just return the token (this would not be done in production)
    return {
        "message": "If the email exists, a password reset link has been sent",
        "debug_token": reset_token  # Remove this in production
    }

@router.post("/reset-password/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    reset_data: PasswordResetSchema,
    db: Session = Depends(get_db)
):
    """
    Confirm a password reset.
    
    - **token**: Password reset token
    - **new_password**: New password to set
    """
    # Find the reset token
    reset_record = db.query(PasswordReset).filter(
        PasswordReset.token == reset_data.token,
        PasswordReset.expires_at > datetime.utcnow(),
        PasswordReset.is_used.is_(False)
    ).first()
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update the user's password
    user = db.query(User).filter(User.id == reset_record.user_id).first()
    user.password_hash = get_password_hash(reset_data.new_password)
    user.updated_at = datetime.utcnow()
    
    # Mark the reset token as used
    reset_record.is_used = True
    reset_record.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password has been reset successfully"}
