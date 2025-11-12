"""
Main FastAPI application for Racing Analytics platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.api.routes import router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Racing Analytics API",
    description="AI-powered racing analytics and strategy platform using the 4-Factor Model",
    version="1.0.0",
)

# Configure CORS for React frontend
# Allow all Vercel deployments and local development
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
production_url = os.getenv("FRONTEND_URL", "https://circuit-fbtth1gml-justin-groszs-projects.vercel.app")
if production_url:
    allowed_origins.append(production_url)

# Also allow any vercel.app subdomain for preview deployments
allowed_origins.append("https://*.vercel.app")

# TEMPORARY: Allow all origins for development
# TODO: Restrict this in production
if os.getenv("CORS_ALLOW_ALL"):
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api prefix
app.include_router(router, prefix="/api")


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
