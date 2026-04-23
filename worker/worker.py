import os
import signal
import time

import redis

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)


def shutdown_handler(signum, frame):
    print("Shutting down gracefully...")
    exit(0)


def process_job(job_id):
    r.hset(f"job:{job_id}", "status", "processing")
    time.sleep(1)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Job {job_id} completed")


signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

while True:
    job = r.brpop("job", timeout=5)
    if job:
        _, job_id = job
        try:
            process_job(job_id.decode())
        except Exception as e:
            print(f"Error processing job {job_id.decode()}: {e}")
            r.hset(f"job:{job_id.decode()}", "status", "failed")
