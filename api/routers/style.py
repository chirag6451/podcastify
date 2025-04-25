"""
Purpose and Objective: 
This module implements API endpoints for style-related entities including
conversation styles, video styles, profile types, and platforms for podcast creation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.style import ConversationStyle, VideoStyle, ProfileType, Platform
from ..schemas.style import (
    ConversationStyleResponse, ConversationStyleCreate,
    VideoStyleResponse, VideoStyleCreate,
    ProfileTypeResponse, ProfileTypeCreate,
    PlatformResponse, PlatformCreate
)
from ..auth import get_current_user
from ..schemas.user import UserResponse

router = APIRouter(
    tags=["styles"],
    responses={404: {"description": "Not found"}}
)

# Conversation Style endpoints
@router.get("/conversation", response_model=List[ConversationStyleResponse])
async def get_conversation_styles(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve all available conversation styles.
    
    Returns a list of conversation styles that can be used for podcast creation.
    """
    styles = db.query(ConversationStyle).all()
    return styles

@router.get("/conversation/{style_id}", response_model=ConversationStyleResponse)
async def get_conversation_style(
    style_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve a specific conversation style by its ID.
    
    - **style_id**: The unique identifier of the conversation style
    
    Returns the conversation style details if found, or a 404 error if not found.
    """
    style = db.query(ConversationStyle).filter(ConversationStyle.id == style_id).first()
    if not style:
        raise HTTPException(status_code=404, detail="Conversation style not found")
    return style

@router.post("/conversation", response_model=ConversationStyleResponse)
async def create_conversation_style(
    style: ConversationStyleCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new conversation style.
    
    - **style**: JSON object containing the new conversation style details
    
    Returns the created conversation style.
    """
    # Check if style with same name already exists
    existing_style = db.query(ConversationStyle).filter(ConversationStyle.name == style.name).first()
    if existing_style:
        raise HTTPException(status_code=400, detail="Conversation style with this name already exists")
    
    new_style = ConversationStyle(**style.model_dump())
    db.add(new_style)
    db.commit()
    db.refresh(new_style)
    return new_style

# Video Style endpoints
@router.get("/video", response_model=List[VideoStyleResponse])
async def get_video_styles(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve all available video styles.
    
    Returns a list of video styles that can be used for podcast video creation.
    """
    styles = db.query(VideoStyle).all()
    return styles

@router.get("/video/{style_id}", response_model=VideoStyleResponse)
async def get_video_style(
    style_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve a specific video style by its ID.
    
    - **style_id**: The unique identifier of the video style
    
    Returns the video style details if found, or a 404 error if not found.
    """
    style = db.query(VideoStyle).filter(VideoStyle.id == style_id).first()
    if not style:
        raise HTTPException(status_code=404, detail="Video style not found")
    return style

@router.post("/video", response_model=VideoStyleResponse)
async def create_video_style(
    style: VideoStyleCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new video style.
    
    - **style**: JSON object containing the new video style details
    
    Returns the created video style.
    """
    # Check if style with same name already exists
    existing_style = db.query(VideoStyle).filter(VideoStyle.name == style.name).first()
    if existing_style:
        raise HTTPException(status_code=400, detail="Video style with this name already exists")
    
    new_style = VideoStyle(**style.model_dump())
    db.add(new_style)
    db.commit()
    db.refresh(new_style)
    return new_style

# Profile Type endpoints
@router.get("/profile-types", response_model=List[ProfileTypeResponse])
async def get_profile_types(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve all available profile types.
    
    Returns a list of profile types that can be used for speaker profiles.
    """
    profile_types = db.query(ProfileType).all()
    return profile_types

@router.get("/profile-types/{profile_type_id}", response_model=ProfileTypeResponse)
async def get_profile_type(
    profile_type_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve a specific profile type by its ID.
    
    - **profile_type_id**: The unique identifier of the profile type
    
    Returns the profile type details if found, or a 404 error if not found.
    """
    profile_type = db.query(ProfileType).filter(ProfileType.id == profile_type_id).first()
    if not profile_type:
        raise HTTPException(status_code=404, detail="Profile type not found")
    return profile_type

@router.post("/profile-types", response_model=ProfileTypeResponse)
async def create_profile_type(
    profile_type: ProfileTypeCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new profile type.
    
    - **profile_type**: JSON object containing the new profile type details
    
    Returns the created profile type.
    """
    # Check if profile type with same name already exists
    existing_profile_type = db.query(ProfileType).filter(ProfileType.name == profile_type.name).first()
    if existing_profile_type:
        raise HTTPException(status_code=400, detail="Profile type with this name already exists")
    
    new_profile_type = ProfileType(**profile_type.model_dump())
    db.add(new_profile_type)
    db.commit()
    db.refresh(new_profile_type)
    return new_profile_type

# Platform endpoints
@router.get("/platforms", response_model=List[PlatformResponse])
async def get_platforms(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve all available platforms.
    
    Returns a list of platforms that can be used for podcast distribution.
    """
    platforms = db.query(Platform).all()
    return platforms

@router.get("/platforms/{platform_id}", response_model=PlatformResponse)
async def get_platform(
    platform_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve a specific platform by its ID.
    
    - **platform_id**: The unique identifier of the platform
    
    Returns the platform details if found, or a 404 error if not found.
    """
    platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform

@router.post("/platforms", response_model=PlatformResponse)
async def create_platform(
    platform: PlatformCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new platform.
    
    - **platform**: JSON object containing the new platform details
    
    Returns the created platform.
    """
    # Check if platform with same name already exists
    existing_platform = db.query(Platform).filter(Platform.name == platform.name).first()
    if existing_platform:
        raise HTTPException(status_code=400, detail="Platform with this name already exists")
    
    new_platform = Platform(**platform.model_dump())
    db.add(new_platform)
    db.commit()
    db.refresh(new_platform)
    return new_platform
