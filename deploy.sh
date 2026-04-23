#!/bin/bash
set -e

TIMEOUT=60
SERVICE="frontend"

echo "Starting rolling update for $SERVICE..."

# Build new image
docker compose build $SERVICE

# Start new container
docker compose up -d --no-deps $SERVICE

# Wait for health check
START=$(date +%s)
while true; do
  CURRENT=$(date +%s)
  ELAPSED=$((CURRENT - START))
  
  if [ $ELAPSED -gt $TIMEOUT ]; then
    echo "Health check timeout after ${TIMEOUT}s - rolling back"
    docker compose restart $SERVICE
    exit 1
  fi
  
  if docker compose ps $SERVICE | grep -q "healthy"; then
    echo "New container is healthy - deployment successful"
    break
  fi
  
  sleep 5
done

echo "Deployment complete"