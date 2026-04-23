#!/bin/bash
set -e

TIMEOUT=60

echo "Starting rolling update..."

# Build all new images
docker compose build

# Rolling update each service one at a time
for SERVICE in api worker frontend; do
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

    STATUS=$(docker compose ps $SERVICE --format json 2>/dev/null | python3 -c "import sys,json; data=sys.stdin.read().strip(); c=json.loads(data.split(chr(10))[0]); print(c.get('Health',''))" 2>/dev/null || echo "unknown")

    if [ "$STATUS" = "healthy" ] || docker compose ps $SERVICE | grep -q "healthy"; then
      echo "$SERVICE is healthy"
      break
    fi

    echo "Waiting for $SERVICE... (${ELAPSED}s)"
    sleep 5
  done
done

echo "All services updated successfully"
