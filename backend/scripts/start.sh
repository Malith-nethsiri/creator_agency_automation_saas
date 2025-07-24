#!/bin/bash

# Start script for production
set -e

echo "Starting Creator Agency Automation SaaS Backend..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers ${WORKERS:-4} \
    --log-level ${LOG_LEVEL:-info} \
    --access-log \
    --no-use-colors
