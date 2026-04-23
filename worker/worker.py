import redis
import time
import os
import signal

# FIX: Use environment variables instead of hardcoded localhost
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)

def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")

# FIX: Added graceful shutdown handler
def shutdown_handler(signum, frame):
    print("Shutting down gracefully...")
    exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

# FIX: Added error handling around job processing
while True:
    job = r.brpop("job", timeout=5)
    if job:
        _, job_id = job
        try:
            process_job(job_id.decode())
        except Exception as e:
            print(f"Error processing job {job_id.decode()}: {e}")
            r.hset(f"job:{job_id.decode()}", "status", "failed")