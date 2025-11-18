"""
Netlify Function wrapper for FastAPI backend.
This allows the entire FastAPI app to run as a serverless function.
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import FastAPI app
from main import app
from mangum import Mangum

# Mangum is an adapter for running ASGI applications (FastAPI) on AWS Lambda and Netlify Functions
handler = Mangum(app, lifespan="off")
