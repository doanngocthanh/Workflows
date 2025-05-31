# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/uploads /app/processed

# Initialize database
RUN python scripts/init_db.py

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "app/main.py"]

# docker-compose.yml
version: '3.8'

services:
  workflow-engine:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/workflow_engine.db
      - DEBUG=true
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
      - ./processed:/app/processed
    restart: unless-stopped

  # Optional: Use PostgreSQL instead of SQLite
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: workflow_engine
  #     POSTGRES_USER: workflow_user
  #     POSTGRES_PASSWORD: workflow_pass
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:

# README.md