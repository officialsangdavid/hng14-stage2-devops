FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
RUN useradd -m -u 1001 -s /bin/bash worker
WORKDIR /app
COPY --from=builder /root/.local /home/worker/.local
COPY --chown=worker:worker . .
USER worker
ENV PATH=/home/worker/.local/bin:$PATH
CMD ["python", "worker.py"]
