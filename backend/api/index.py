"""
Vercel serverless function wrapper for FastAPI application.
This file adapts the FastAPI app to work with Vercel's serverless platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
from pathlib import Path

# Add parent directory to path so we can import from backend
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import the main FastAPI app
from main import app

# Wrap the FastAPI app with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")
