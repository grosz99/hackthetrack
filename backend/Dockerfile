FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Start command
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
