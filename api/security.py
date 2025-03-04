from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable - use X-API-Key from env
API_KEY = os.getenv("X-API-Key", "indapoint2025")  # Using the key from .env

# Define API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify the API key provided in request header"""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key
