# Multi-stage Dockerfile for Smart SPC Backend

# Stage 1: Base image with dependencies
FROM python:3.11-slim as base
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development
FROM base as development
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

# Development command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Stage 3: Production
FROM base as production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install production server
RUN pip install gunicorn

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create directories
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

# Production command
CMD ["gunicorn", "smart_spc.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
