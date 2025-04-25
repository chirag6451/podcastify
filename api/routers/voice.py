"""
Purpose and Objective: 
This module implements API endpoints for Elevenlabs voice data, allowing retrieval
and filtering of available voices for podcast creation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.voice import ElevenlabsVoice
from ..schemas.voice import VoiceResponse, VoiceFilter
from ..auth import get_current_user
from ..schemas.user import UserResponse

router = APIRouter(
    tags=["voices"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[VoiceResponse])
async def get_voices(
    gender: Optional[str] = Query(None, description="Filter by gender (e.g., male, female)"),
    accent: Optional[str] = Query(None, description="Filter by accent (e.g., american, british)"),
    age: Optional[str] = Query(None, description="Filter by age (e.g., young, middle-aged)"),
    language: Optional[str] = Query(None, description="Filter by language (e.g., en, es)"),
    use_case: Optional[str] = Query(None, description="Filter by use case (e.g., podcast, audiobook)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g., premade, cloned)"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve all available Elevenlabs voices with optional filtering.
    
    - **gender**: Filter by voice gender
    - **accent**: Filter by voice accent
    - **age**: Filter by voice age
    - **language**: Filter by voice language
    - **use_case**: Filter by voice use case
    - **category**: Filter by voice category
    
    Returns a list of voices matching the specified filters.
    """
    query = db.query(ElevenlabsVoice)
    
    if gender:
        query = query.filter(ElevenlabsVoice.gender == gender)
    if accent:
        query = query.filter(ElevenlabsVoice.accent == accent)
    if age:
        query = query.filter(ElevenlabsVoice.age == age)
    if language:
        query = query.filter(ElevenlabsVoice.language == language)
    if use_case:
        query = query.filter(ElevenlabsVoice.use_case == use_case)
    if category:
        query = query.filter(ElevenlabsVoice.category == category)
    
    voices = query.all()
    return voices

@router.get("/{voice_id}", response_model=VoiceResponse)
async def get_voice(
    voice_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve a specific Elevenlabs voice by its ID.
    
    - **voice_id**: The unique identifier of the voice
    
    Returns the voice details if found, or a 404 error if not found.
    """
    voice = db.query(ElevenlabsVoice).filter(ElevenlabsVoice.voice_id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice

@router.post("/filter", response_model=List[VoiceResponse])
async def filter_voices(
    filter_params: VoiceFilter,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Filter voices using a request body instead of query parameters.
    Useful for more complex filtering requirements.
    
    - **filter_params**: JSON object containing filter criteria
    
    Returns a list of voices matching the specified filters.
    """
    query = db.query(ElevenlabsVoice)
    
    if filter_params.gender:
        query = query.filter(ElevenlabsVoice.gender == filter_params.gender)
    if filter_params.accent:
        query = query.filter(ElevenlabsVoice.accent == filter_params.accent)
    if filter_params.age:
        query = query.filter(ElevenlabsVoice.age == filter_params.age)
    if filter_params.language:
        query = query.filter(ElevenlabsVoice.language == filter_params.language)
    if filter_params.use_case:
        query = query.filter(ElevenlabsVoice.use_case == filter_params.use_case)
    if filter_params.category:
        query = query.filter(ElevenlabsVoice.category == filter_params.category)
    
    voices = query.all()
    return voices
