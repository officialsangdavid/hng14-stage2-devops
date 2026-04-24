# DevOps - Containerized Microservices Application

## Overview

This project takes a broken multi-service application and fixes it, containerizes it with Docker, and ships it with a full 6-stage CI/CD pipeline on GitHub Actions. The stack consists of a Node.js frontend, a FastAPI backend, a Python worker, and Redis as a job queue.

## Architecture
[User] -> [Frontend :3000] -> [API :8000] -> [Redis]
^
[Worker]

- **Frontend** - Node.js/Express app on port 3000. Accepts job submissions and proxies status checks to the API.
- **API** - FastAPI/Python app on port 8000. Creates jobs, stores them in Redis, returns status.
- **Worker** - Python process. Listens on Redis queue, processes jobs, updates status.
- **Redis** - In-memory job queue and state store. Internal only, not exposed to the host.

---

## Project Structure
devops/
├── api/                    # FastAPI Python backend
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── .dockerignore
│   └── tests/
│       └── test_api.py
├── frontend/               # Node.js/Express frontend
│   ├── Dockerfile
│   ├── app.js
│   ├── package.json
│   └── .dockerignore
├── worker/                 # Python job worker
│   ├── Dockerfile
│   ├── worker.py
│   ├── requirements.txt
│   └── .dockerignore
├── .github/
│   └── workflows/
│       └── pipeline.yml    # CI/CD pipeline
├── docker-compose.yml      # Full stack orchestration
├── deploy.sh               # Rolling update deploy script
├── .env.example            # Environment variable template
├── FIXES.md                # All bugs found and fixed
└── README.md               # This file

---

## Prerequisites

Before you begin, make sure you have the following installed on your machine:

- **Git** - to clone the repository
- **Docker** >= 24.0 - to build and run containers
- **Docker Compose** >= 2.0 (v2, included with Docker Desktop)
- **curl** - to test endpoints (optional but recommended)

To verify your installations:

```bash
git --version
docker --version
docker compose version
```

---

## How to Bring the Stack Up on a Clean Machine

### Step 1: Clone the Repository

```bash
git clone https://github.com/officialsangdavid/project-repo
cd project-0cloned
```

### Step 2: Set Up Environment Variables

```bash
cp .env.example .env
```

The default values in `.env.example` work out of the box for local development. No changes needed.

### Step 3: Build and Start All Services

```bash
docker compose up -d --build
```

This command will:
- Build Docker images for the frontend, API, and worker
- Pull the official Redis image from Docker Hub
- Start all 4 containers in detached mode
- Run health checks on each service before marking them ready

### Step 4: Wait for Services to Be Healthy

Wait approximately 30 seconds, then run:

```bash
docker compose ps
```

### What a Successful Startup Looks Like
NAME               IMAGE                          STATUS
devops-api-1       devops-api        Up (healthy)
devops-frontend-1   frontend   Up (healthy)
devops-redis-1      redis:7-alpine                 Up (healthy)
devops-worker-1    devops-worker     Up

All services should show Up and the API, frontend, and Redis should show (healthy).

---

## Verifying the Application Works

### Check Health Endpoints

```bash
# Frontend health
curl http://localhost:3000/health
# Expected: {"status":"healthy"}

# API health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Submit a Job

```bash
curl -X POST http://localhost:3000/submit
# Expected: {"job_id":"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
```

### Check Job Status

```bash
# Replace JOB_ID with the job_id from the previous response
curl http://localhost:3000/status/JOB_ID
# Expected: {"job_id":"...","status":"completed"}
```

The status will transition from queued to processing to completed within a few seconds.

### Check Logs

```bash
# View all logs
docker compose logs

# View logs for a specific service
docker compose logs api
docker compose logs worker
docker compose logs frontend
```

---

## Bugs Fixed

All bugs found and fixed are documented in detail in FIXES.md.

Summary of issues found in the original source code:

- Redis connection hardcoded to localhost in both API and Worker
- API URL hardcoded to localhost in Frontend
- Missing /health endpoints in API and Frontend
- Frontend not binding to 0.0.0.0
- Unpinned dependency versions in requirements.txt
- Missing error handling in Worker job processing
- Unused signal import in Worker with no graceful shutdown
- Missing .dockerignore files
- No test suite

---

## CI/CD Pipeline

The GitHub Actions pipeline at .github/workflows/pipeline.yml runs automatically on every push to main or develop and on pull requests to main.

### Pipeline Stages

**Stage 1 - Lint**
- Runs flake8 on all Python code (API and Worker)
- Runs eslint on JavaScript (Frontend)
- Runs hadolint on all three Dockerfiles

**Stage 2 - Test**
- Spins up a Redis service container
- Installs Python dependencies
- Runs pytest with coverage report
- Uploads coverage report as artifact

**Stage 3 - Security Scan**
- Builds all three Docker images
- Runs Trivy vulnerability scanner on each image
- Reports CRITICAL severity findings

**Stage 4 - Build**
- Builds all three Docker images tagged with the git SHA and latest
- Verifies images exist

**Stage 5 - Integration Test**
- Starts the full stack with docker compose up
- Waits up to 60 seconds for all services to be healthy
- Tests health endpoints
- Submits a real job and polls until it reaches completed status
- Tears down the stack

**Stage 6 - Deploy** (main branch only)
- Builds updated images
- Runs rolling update via deploy.sh
- Updates API, frontend, and worker one at a time
- Each service must be healthy before moving to the next
- Aborts and exits with error if any service fails health check within 60 seconds
- Verifies frontend is healthy after full deployment

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| REDIS_HOST | redis | Redis service hostname (Docker service name) |
| REDIS_PORT | 6379 | Redis port |
| API_URL | http://api:8000 | Internal API URL for frontend proxy |
| NODE_ENV | production | Node.js environment |

---

## Tearing Down

```bash
# Stop and remove all containers, networks, and volumes
docker compose down -v

# Also remove built images (full cleanup)
docker compose down -v --rmi all
```

---

## Notes

- Redis is never exposed to the host machine - it is only accessible within the Docker network
- All services run as non-root users inside their containers
- Multi-stage Docker builds are used for API and Frontend to minimize image size
- The Worker has no HTTP health endpoint - it is monitored by checking if the process is running
ENDOFFILE

git add README.md
git commit -m "docs: add comprehensive README with full setup guide"
git push origin main
