#!/bin/bash
set -e

TIMEOUT=60

echo "Starting rolling update..."

docker compose build

for SERVICE in api frontend; do
  echo "Updating $SERVICE..."
  docker compose up -d --no-deps $SERVICE

  START=$(date +%s)
  while true; do
    CURRENT=$(date +%s)
    ELAPSED=$((CURRENT - START))

    if [ $ELAPSED -gt $TIMEOUT ]; then
      echo "Health check timeout for $SERVICE after ${TIMEOUT}s - aborting"
      exit 1
    fi

    if docker compose ps $SERVICE | grep -q "healthy"; then
      echo "$SERVICE is healthy"
      break
    fi

    echo "Waiting for $SERVICE... (${ELAPSED}s)"
    sleep 5
  done
done

# Worker has no HTTP endpoint - just start it and verify it's running
echo "Updating worker..."
docker compose up -d --no-deps worker
sleep 5
if docker compose ps worker | grep -q "Up"; then
  echo "worker is running"
else
  echo "worker failed to start"
  exit 1
fi

echo "All services updated successfully"
