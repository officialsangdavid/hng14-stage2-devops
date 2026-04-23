import os
import uuid

import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)


@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="unhealthy")


@app.post("/submit")
def submit_job():
    job_id = str(uuid.uuid4())
    r.hset(f"job:{job_id}", "status", "queued")
    r.lpush("job", job_id)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": status.decode()}
