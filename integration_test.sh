#!/bin/bash
set -e

TIMEOUT=60
BASE_URL="http://localhost:3000"

echo "Starting integration test..."

# Wait for services
echo "Waiting for services to be healthy..."
timeout $TIMEOUT bash -c "until curl -sf $BASE_URL/health; do sleep 2; done"

# Test health endpoints
echo "Testing health endpoints..."
curl -sf $BASE_URL/health
curl -sf http://localhost:8000/health

# Submit a job
echo "Submitting job..."
JOB_RESPONSE=$(curl -sf -X POST $BASE_URL/submit)
echo "Response: $JOB_RESPONSE"
JOB_ID=$(echo $JOB_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"

# Poll for completion
echo "Polling for job completion..."
for i in {1..30}; do
  STATUS=$(curl -sf $BASE_URL/status/$JOB_ID | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")
  echo "Attempt $i: status=$STATUS"
  if [ "$STATUS" = "completed" ]; then
    echo "Integration test passed!"
    exit 0
  fi
  sleep 2
done

echo "Integration test failed - job did not complete"
exit 1
