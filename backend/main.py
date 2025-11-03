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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:5174",  # Vite alternative port
        "http://localhost:5175",  # Vite alternative port 2
        "http://localhost:3000",  # Alternative React port
        "http://localhost:8000",  # Backend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


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
