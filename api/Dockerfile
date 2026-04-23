FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
# Install wget for health check
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1001 apiuser
WORKDIR /app
COPY --from=builder /root/.local /home/apiuser/.local
COPY --chown=apiuser:apiuser . .
USER apiuser
ENV PATH=/home/apiuser/.local/bin:$PATH
EXPOSE 8000

# Use wget for health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]