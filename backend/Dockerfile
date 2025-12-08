# backend/Dockerfile

# 1. Use a lightweight "Slim" Linux version with Python 3.11 pre-installed
FROM python:3.11-slim

# 2. Set environment variables
# Prevents Python from writing temporary files (.pyc) to disk
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures logs are pushed to the console immediately (crucial for debugging)
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 3. Install system dependencies
# We need 'gcc' and 'libpq-dev' to build the connection tool for PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python libraries
# We copy this first to leverage Docker caching (speeds up builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the actual application code
COPY . .

# 6. Default Command
# This runs migrations (alembic) and then starts the server
# Note: No "--reload" flag here! That is for development only.
CMD sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"