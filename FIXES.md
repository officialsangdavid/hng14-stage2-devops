# Bug Fixes and Issues Found

## Bug 1: Redis connection hardcoded to localhost in API

- **File**: `api/main.py`
- **Line**: 8
- **Issue**: Redis client connects to `localhost:6379` which will fail inside Docker containers. Services in Docker networks communicate via service names, not localhost.
- **Fix**: Changed to use environment variable with service name as default
- **Code Change**:
```python
# Before:
r = redis.Redis(host="localhost", port=6379)

# After:
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)
```

---

## Bug 2: Redis connection hardcoded to localhost in Worker

- **File**: `worker/worker.py`
- **Line**: 6
- **Issue**: Same as Bug 1 - worker cannot connect to Redis inside Docker network using localhost
- **Fix**: Changed to use environment variable
- **Code Change**:
```python
# Before:
r = redis.Redis(host="localhost", port=6379)

# After:
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)
```

---

## Bug 3: API URL hardcoded to localhost in Frontend
- **File**: `frontend/app.js`
- **Line**: 6
- **Issue**: API_URL points to `localhost:8000` which doesn't work in Docker. Frontend container cannot reach API at localhost - must use service name.
- **Fix**: Changed to use environment variable
- **Code Change**:
```javascript
// Before:
const API_URL = "http://localhost:8000";

// After:
const API_URL = process.env.API_URL || "http://api:8000";
```

---

## Bug 4: Missing health check endpoint in API
- **File**: `api/main.py`
- **Line**: N/A (missing entirely)
- **Issue**: No health endpoint for Docker HEALTHCHECK or monitoring. Pipeline requires this.
- **Fix**: Added /health endpoint
- **Code Change**:
```python
# Add after line 8:
@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "healthy"}
    except:
        return {"status": "unhealthy"}, 503
```

---

## Bug 5: Missing health check endpoint in Frontend
- **File**: `frontend/app.js`
- **Line**: N/A (missing entirely)
- **Issue**: No health endpoint for Docker HEALTHCHECK
- **Fix**: Added /health endpoint
- **Code Change**:
```javascript
// Add before app.listen():
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});
```

---

## Bug 6: Frontend not binding to all interfaces
- **File**: `frontend/app.js`
- **Line**: 29
- **Issue**: app.listen(3000) defaults to 127.0.0.1 which is only accessible from inside the container. Must bind to 0.0.0.0 to accept external connections.
- **Fix**: Explicitly bind to 0.0.0.0
- **Code Change**:
```javascript
// Before:
app.listen(3000, () => {
  console.log('Frontend running on port 3000');
});

// After:
app.listen(3000, '0.0.0.0', () => {
  console.log('Frontend running on 0.0.0.0:3000');
});
```

---

## Bug 7: No version pinning in API requirements.txt
- **File**: `api/requirements.txt`
- **Lines**: 1-3
- **Issue**: Dependencies not pinned to specific versions. This can cause build failures or unexpected behavior when package versions change.
- **Fix**: Pinned all dependencies to specific versions
- **Code Change**:
```
# Before:
fastapi
uvicorn
redis

# After:
fastapi==0.104.1
uvicorn[standard]==0.24.0
redis==5.0.1
```

---

## Bug 8: No version pinning in Worker requirements.txt
- **File**: `worker/requirements.txt`
- **Line**: 1
- **Issue**: Same as Bug 7
- **Fix**: Pinned redis version
- **Code Change**:
```
# Before:
redis

# After:
redis==5.0.1
```

---

## Bug 9: Missing error handling in Worker job processing
- **File**: `worker/worker.py`
- **Line**: 14-18
- **Issue**: If process_job() throws an exception, the job is lost and worker may crash. No try-catch around job processing.
- **Fix**: Added try-catch block with error status update
- **Code Change**:
```python
# Before:
while True:
    job = r.brpop("job", timeout=5)
    if job:
        _, job_id = job
        process_job(job_id.decode())

# After:
while True:
    job = r.brpop("job", timeout=5)
    if job:
        _, job_id = job
        try:
            process_job(job_id.decode())
        except Exception as e:
            print(f"Error processing job {job_id.decode()}: {e}")
            r.hset(f"job:{job_id.decode()}", "status", "failed")
```

---

## Bug 10: Unused import in Worker
- **File**: `worker/worker.py`
- **Line**: 4
- **Issue**: `import signal` is imported but never used. Code quality issue - suggests incomplete implementation of graceful shutdown.
- **Fix**: Either remove the import or implement graceful shutdown (I implemented shutdown)
- **Code Change**:
```python
# Added signal handler for graceful shutdown:
def shutdown_handler(signum, frame):
    print("Shutting down gracefully...")
    exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

---

## Bug 11: Missing .dockerignore files
- **File**: N/A (files don't exist)
- **Issue**: Without .dockerignore, Docker COPY commands will include unnecessary files (node_modules, __pycache__, .git, .env) in the image, bloating it and potentially exposing secrets.
- **Fix**: Created .dockerignore in each service directory
- **Content**:
```
node_modules/
__pycache__/
*.pyc
.git/
.env
.env.*
!.env.example
*.log
.pytest_cache/
coverage/
dist/
build/
.vscode/
.idea/
```

---

## Bug 12: No test directory or tests
- **File**: N/A (missing)
- **Issue**: Pipeline requires pytest tests, but no tests/ directory exists in API
- **Fix**: Created `api/tests/` directory with 3 unit tests
- **Created**: `api/tests/test_api.py` with tests for:
  - create_job endpoint
  - get_job endpoint
  - health endpoint