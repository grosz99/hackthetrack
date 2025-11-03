"""
Vercel serverless function entry point for FastAPI backend.
"""

import sys
import os
from pathlib import Path

# Set up paths for Vercel serverless environment
BASE_DIR = Path(__file__).resolve().parent.parent
backend_dir = BASE_DIR / "backend"
sys.path.insert(0, str(backend_dir))

# Set database path
db_path = BASE_DIR / "circuit-fit.db"
os.environ["DATABASE_PATH"] = str(db_path)

# Import FastAPI app
from main import app

# Export the FastAPI app directly for Vercel
# Vercel's Python runtime will handle the ASGI/WSGI wrapping
__all__ = ["app"]
