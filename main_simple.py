"""
Purpose and Objective: 
This is a simplified FastAPI application entry point for the podcast creation platform.
It configures the FastAPI app, sets up middleware, and includes all API routes.
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

# Add the project root to the Python path to fix imports
sys.path.insert(0, str(Path(__file__).parent))

# Import routers
from api.auth_routes import router as auth_router
from api.user_routes import router as user_router
from api.payment_routes import router as payment_router
from api.podcast_routes import router as podcast_router
from api.logger import api_logger

# Initialize FastAPI app
app = FastAPI(
    title="PodcastAI API",
    description="API for PodcastAI - Create and manage podcasts with AI",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom exception handler for all exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    error_detail = str(exc)
    api_logger.error(f"Unhandled exception: {error_detail}")
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail}
    )

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(payment_router)
app.include_router(podcast_router)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    port = 8012
    api_logger.info(f"Starting PodcastAI API server on port {port}")
    uvicorn.run("main_simple:app", host="0.0.0.0", port=port, reload=True)
