from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from fastapi.security import OAuth2PasswordBearer
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime, timedelta
import json
import httpx
from typing import Optional, Dict
from create_audio.db_utils import PodcastDB
from .models import GoogleAuthResponse, GoogleAuthRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration for Google OAuth
CLIENT_ID = '577155825398-pg20jk65d3ksgf16vbtirnmvraq8kvff.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:3000'
TOKEN_URI = 'https://oauth2.googleapis.com/token'

@router.post("/auth/google/callback", response_model=GoogleAuthResponse)
async def google_auth_callback(request: GoogleAuthRequest):
    """
    Handle Google OAuth callback and store user data
    """
    try:
        # Exchange authorization code for tokens
        try:
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    TOKEN_URI,
                    data={
                        'client_id': CLIENT_ID,
                        'client_secret': CLIENT_SECRET,
                        'code': request.code,
                        'redirect_uri': REDIRECT_URI,
                        'grant_type': 'authorization_code'
                    }
                )
                token_data = token_response.json()
                logger.info(f"Got token data: {token_data}")
                
                if 'error' in token_data:
                    raise Exception(f"Token error: {token_data['error']}")
                
                access_token = token_data['access_token']
                refresh_token = token_data.get('refresh_token')
                
                # Get user info using the access token
                user_response = await client.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info = user_response.json()
                logger.info(f"Got user info: {user_info}")
                
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Store in database
        try:
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO google_auth (
                            user_id,
                            email,
                            google_id,
                            access_token,
                            refresh_token,
                            token_uri,
                            client_id,
                            client_secret,
                            profile_data
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (email) DO UPDATE SET 
                            user_id = EXCLUDED.user_id,
                            google_id = EXCLUDED.google_id,
                            access_token = EXCLUDED.access_token,
                            refresh_token = EXCLUDED.refresh_token,
                            token_uri = EXCLUDED.token_uri,
                            client_id = EXCLUDED.client_id,
                            client_secret = EXCLUDED.client_secret,
                            profile_data = EXCLUDED.profile_data,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        user_info['sub'],  # Using Google's sub field as user_id
                        user_info['email'],
                        user_info['sub'],  # Using sub as google_id too
                        access_token,
                        refresh_token,
                        TOKEN_URI,
                        CLIENT_ID,
                        CLIENT_SECRET,
                        json.dumps(user_info)
                    ))
                    conn.commit()
                    logger.info(f"Saved user data")
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        response_data = GoogleAuthResponse(
            success=True,
            user_id=user_info['sub'],
            email=user_info['email'],
            name=user_info.get('name'),
            picture=user_info.get('picture')
        )
        logger.info(f"Sending response: {response_data}")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/google/refresh")
async def refresh_token(user_id: str = Query(..., description="User ID to refresh token for")):
    """
    Get the stored Google token for a user
    """
    try:
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT access_token, token_expiry
                    FROM google_auth WHERE user_id = %s
                """, (user_id,))
                result = cur.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="User not found")
                    
                access_token, token_expiry = result
                
                # Check if token is expired
                if token_expiry and token_expiry < datetime.utcnow():
                    raise HTTPException(status_code=401, detail="Token expired")
                
                return {"success": True, "access_token": access_token}
                
    except Exception as e:
        logger.error(f"Error in refresh_token: {e}")
        raise HTTPException(status_code=400, detail=str(e))

def get_user_info(credentials):
    """Get user info from Google using the provided credentials"""
    import google.auth.transport.requests
    import requests
    
    try:
        session = requests.Session()
        auth_req = google.auth.transport.requests.Request(session=session)
        
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        response = requests.get(
            userinfo_endpoint,
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get user info: {str(e)}")
