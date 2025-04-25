"""
Purpose and Objective: 
This module defines FastAPI router for podcast-related endpoints including
podcast management, episode management, and podcast group organization.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..auth import get_current_user
from ..models.user import User
from ..models.podcast import Podcast, Episode, PodcastGroup, PodcastPlatformConfig
from ..schemas.podcast import (
    PodcastCreate, PodcastResponse, PodcastUpdate,
    EpisodeCreate, EpisodeResponse, EpisodeUpdate,
    PodcastGroupCreate, PodcastGroupResponse,
    PlatformConfigCreate, PlatformConfigResponse
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Create router
router = APIRouter()

# ==================== Podcast Group Endpoints ====================

@router.post("/groups", response_model=PodcastGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_podcast_group(
    group: PodcastGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new podcast group.
    
    Args:
        group: Podcast group data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created podcast group
    """
    try:
        new_group = PodcastGroup(**group.model_dump(), user_id=current_user.id)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/groups", response_model=List[PodcastGroupResponse])
async def get_podcast_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Get all podcast groups for the current user.
    
    Args:
        db: Database session
        current_user: Authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of podcast groups
    """
    return db.query(PodcastGroup).filter(PodcastGroup.user_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/groups/{group_id}", response_model=PodcastGroupResponse)
async def get_podcast_group(
    group_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific podcast group by ID.
    
    Args:
        group_id: Podcast group ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Podcast group
    """
    group = db.query(PodcastGroup).filter(
        PodcastGroup.id == group_id,
        PodcastGroup.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast group not found"
        )
    
    return group

@router.put("/groups/{group_id}", response_model=PodcastGroupResponse)
async def update_podcast_group(
    group_data: PodcastGroupCreate,
    group_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a podcast group.
    
    Args:
        group_data: Updated podcast group data
        group_id: Podcast group ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated podcast group
    """
    group = db.query(PodcastGroup).filter(
        PodcastGroup.id == group_id,
        PodcastGroup.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast group not found"
        )
    
    try:
        for key, value in group_data.model_dump().items():
            setattr(group, key, value)
        
        group.updated_at = datetime.now()
        db.commit()
        db.refresh(group)
        return group
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_podcast_group(
    group_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a podcast group.
    
    Args:
        group_id: Podcast group ID
        db: Database session
        current_user: Authenticated user
    """
    group = db.query(PodcastGroup).filter(
        PodcastGroup.id == group_id,
        PodcastGroup.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast group not found"
        )
    
    try:
        db.delete(group)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# ==================== Podcast Endpoints ====================

@router.post("/", response_model=PodcastResponse, status_code=status.HTTP_201_CREATED)
async def create_podcast(
    podcast: PodcastCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new podcast.
    
    Args:
        podcast: Podcast data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created podcast
    """
    try:
        new_podcast = Podcast(**podcast.model_dump(), user_id=current_user.id)
        db.add(new_podcast)
        db.commit()
        db.refresh(new_podcast)
        return new_podcast
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/", response_model=List[PodcastResponse])
async def get_podcasts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Get all podcasts for the current user, optionally filtered by group ID.
    
    Args:
        db: Database session
        current_user: Authenticated user
        group_id: Optional group ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of podcasts
    """
    query = db.query(Podcast).filter(Podcast.user_id == current_user.id)
    
    if group_id:
        query = query.filter(Podcast.group_id == group_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{podcast_id}", response_model=PodcastResponse)
async def get_podcast(
    podcast_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific podcast by ID.
    
    Args:
        podcast_id: Podcast ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Podcast
    """
    podcast = db.query(Podcast).filter(
        Podcast.id == podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found"
        )
    
    return podcast

@router.put("/{podcast_id}", response_model=PodcastResponse)
async def update_podcast(
    podcast_data: PodcastUpdate,
    podcast_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a podcast.
    
    Args:
        podcast_data: Updated podcast data
        podcast_id: Podcast ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated podcast
    """
    podcast = db.query(Podcast).filter(
        Podcast.id == podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found"
        )
    
    try:
        for key, value in podcast_data.model_dump(exclude_unset=True).items():
            setattr(podcast, key, value)
        
        podcast.updated_at = datetime.now()
        db.commit()
        db.refresh(podcast)
        return podcast
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/{podcast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_podcast(
    podcast_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a podcast.
    
    Args:
        podcast_id: Podcast ID
        db: Database session
        current_user: Authenticated user
    """
    podcast = db.query(Podcast).filter(
        Podcast.id == podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found"
        )
    
    try:
        db.delete(podcast)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# ==================== Episode Endpoints ====================

# Important: Reordering routes to ensure specific routes with path parameters come before general routes
# This prevents FastAPI from misinterpreting the path parameters

@router.get("/episodes/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific episode by ID.
    
    Args:
        episode_id: Episode ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Episode
    """
    # Join with podcast to check user ownership
    episode = db.query(Episode).join(Podcast).filter(
        Episode.id == episode_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    return episode

@router.get("/episodes", response_model=List[EpisodeResponse])
async def get_episodes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    podcast_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None)
):
    """
    Get all episodes, optionally filtered by podcast ID and status.
    
    Args:
        db: Database session
        current_user: Authenticated user
        podcast_id: Optional podcast ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional status to filter by (e.g., 'draft', 'published')
        
    Returns:
        List of episodes
    """
    # Build query to get episodes from user's podcasts
    query = db.query(Episode).join(Podcast).filter(Podcast.user_id == current_user.id)
    
    # Apply filters if provided
    if podcast_id:
        query = query.filter(Episode.podcast_id == podcast_id)
    
    if status:
        query = query.filter(Episode.status == status)
    
    return query.offset(skip).limit(limit).all()

@router.post("/episodes", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
async def create_episode(
    episode: EpisodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new episode.
    
    Args:
        episode: Episode data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created episode
    """
    # Check if podcast exists and belongs to user
    podcast = db.query(Podcast).filter(
        Podcast.id == episode.podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found or does not belong to user"
        )
    
    try:
        new_episode = Episode(**episode.model_dump())
        db.add(new_episode)
        db.commit()
        db.refresh(new_episode)
        return new_episode
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.put("/episodes/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_data: EpisodeUpdate,
    episode_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an episode.
    
    Args:
        episode_data: Updated episode data
        episode_id: Episode ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated episode
    """
    # Join with podcast to check user ownership
    episode = db.query(Episode).join(Podcast).filter(
        Episode.id == episode_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    try:
        for key, value in episode_data.model_dump(exclude_unset=True).items():
            setattr(episode, key, value)
        
        episode.updated_at = datetime.now()
        db.commit()
        db.refresh(episode)
        return episode
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/episodes/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(
    episode_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an episode.
    
    Args:
        episode_id: Episode ID
        db: Database session
        current_user: Authenticated user
    """
    # Join with podcast to check user ownership
    episode = db.query(Episode).join(Podcast).filter(
        Episode.id == episode_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    try:
        db.delete(episode)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# ==================== Platform Config Endpoints ====================

# Important: Reordering routes to ensure specific routes with path parameters come before general routes
@router.get("/platform-configs/{config_id}", response_model=PlatformConfigResponse)
async def get_platform_config(
    config_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific platform configuration by ID.
    
    Args:
        config_id: Platform configuration ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Platform configuration
    """
    # Join with podcast to check user ownership
    config = db.query(PodcastPlatformConfig).join(Podcast).filter(
        PodcastPlatformConfig.id == config_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform configuration not found"
        )
    
    return config

@router.get("/platform-configs", response_model=List[PlatformConfigResponse])
async def get_platform_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    podcast_id: Optional[int] = Query(None),
    platform_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Get all platform configurations for the current user, optionally filtered by podcast ID and platform ID.
    
    Args:
        db: Database session
        current_user: Authenticated user
        podcast_id: Optional podcast ID to filter by
        platform_id: Optional platform ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of platform configurations
    """
    # Build query to get platform configs from user's podcasts
    query = db.query(PodcastPlatformConfig).join(Podcast).filter(Podcast.user_id == current_user.id)
    
    # Apply filters if provided
    if podcast_id:
        query = query.filter(PodcastPlatformConfig.podcast_id == podcast_id)
    
    if platform_id:
        query = query.filter(PodcastPlatformConfig.platform_id == platform_id)
    
    return query.offset(skip).limit(limit).all()

@router.post("/platform-configs", response_model=PlatformConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_platform_config(
    config: PlatformConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new platform configuration for a podcast.
    
    Args:
        config: Platform configuration data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created platform configuration
    """
    # Check if podcast exists and belongs to user
    podcast = db.query(Podcast).filter(
        Podcast.id == config.podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found or does not belong to user"
        )
    
    # Check if platform config already exists for this podcast and platform
    existing_config = db.query(PodcastPlatformConfig).filter(
        PodcastPlatformConfig.podcast_id == config.podcast_id,
        PodcastPlatformConfig.platform_id == config.platform_id
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Platform configuration already exists for this podcast"
        )
    
    try:
        new_config = PodcastPlatformConfig(**config.model_dump())
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.put("/platform-configs/{config_id}", response_model=PlatformConfigResponse)
async def update_platform_config(
    config_data: PlatformConfigCreate,
    config_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a platform configuration.
    
    Args:
        config_data: Updated platform configuration data
        config_id: Platform configuration ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated platform configuration
    """
    # Join with podcast to check user ownership
    config = db.query(PodcastPlatformConfig).join(Podcast).filter(
        PodcastPlatformConfig.id == config_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform configuration not found"
        )
    
    try:
        for key, value in config_data.model_dump().items():
            setattr(config, key, value)
        
        db.commit()
        db.refresh(config)
        return config
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/platform-configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_platform_config(
    config_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a platform configuration.
    
    Args:
        config_id: Platform configuration ID
        db: Database session
        current_user: Authenticated user
    """
    # Join with podcast to check user ownership
    config = db.query(PodcastPlatformConfig).join(Podcast).filter(
        PodcastPlatformConfig.id == config_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform configuration not found"
        )
    
    try:
        db.delete(config)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
