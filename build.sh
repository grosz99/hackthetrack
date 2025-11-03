#!/bin/bash
# Vercel build script for React + FastAPI monorepo
# This script is executed during Vercel deployment

set -e  # Exit on error

echo "Starting Vercel build process..."

# Step 1: Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Step 2: Build frontend
echo "Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Build complete! Frontend output in frontend/dist/"
echo "Python dependencies installed for serverless functions"

# Verify build outputs
if [ ! -d "frontend/dist" ]; then
    echo "ERROR: Frontend build failed - dist directory not found"
    exit 1
fi

if [ ! -f "circuit-fit.db" ]; then
    echo "ERROR: Database file not found"
    exit 1
fi

echo "Build verification passed!"
