"""
Vercel serverless function wrapper for FastAPI application.
This file adapts the FastAPI app to work with Vercel's serverless platform.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from backend
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import the main FastAPI app
from main import app

# Import Mangum after app to avoid circular imports
from mangum import Mangum

# Wrap the FastAPI app with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")

# Vercel requires this export
def handler_wrapper(event, context):
    """Wrapper function for Vercel serverless deployment."""
    return handler(event, context)
