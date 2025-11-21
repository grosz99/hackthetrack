"""
Main FastAPI application for Racing Analytics platform.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging

from app.api.routes import router
from app.utils.errors import AppError

# Load environment variables
load_dotenv()

# Validate critical environment variables at startup
required_env_vars = ["ANTHROPIC_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Racing Analytics API",
    description="AI-powered racing analytics and strategy platform using the 4-Factor Model",
    version="1.0.0",
)

# Configure CORS for React frontend
# Allow Netlify deployments and local development
allowed_origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",  # Vite alternative port
    "http://localhost:5175",  # Vite alternative port 2
    "http://localhost:5176",  # Vite alternative port 3
    "http://localhost:5177",  # Vite alternative port 4
    "http://localhost:3000",  # Alternative React port
    "http://localhost:8000",  # Backend port
]

# Add production URLs from environment or defaults
production_url = os.getenv("FRONTEND_URL", "https://gibbs-ai.netlify.app")
if production_url:
    allowed_origins.append(production_url)

# Also allow any netlify.app subdomain for preview deployments
allowed_origins.append("https://*.netlify.app")

# TEMPORARY: Allow all origins for development
# TODO: Remove CORS_ALLOW_ALL from Heroku config after verifying Netlify works
if os.getenv("CORS_ALLOW_ALL"):
    allowed_origins = ["*"]
    logger.warning("CORS_ALLOW_ALL is enabled - all origins allowed (development only)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.netlify\.app",  # Allow all Netlify preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api prefix
app.include_router(router, prefix="/api")


# Error handlers
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Handle custom application errors."""
    logger.error(f"{exc.status_code}: {exc.message} [{request.url.path}]")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "path": str(request.url.path)}
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """Handle unexpected errors without exposing internal details."""
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "path": str(request.url.path)}
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Racing Analytics API",
        "version": "1.0.0",
        "theme": "Making the Predictable Unpredictable",
        "docs": "/docs",
        "endpoints": {
            "tracks": "/api/tracks",
            "drivers": "/api/drivers",
            "predict": "/api/predict",
            "chat": "/api/chat",
            "telemetry": "/api/telemetry/compare",
            "health": "/api/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
