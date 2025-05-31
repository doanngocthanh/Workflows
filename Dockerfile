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
#RUN python scripts/init_db.py || python scripts/init_db.py

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "app/main.py"]

