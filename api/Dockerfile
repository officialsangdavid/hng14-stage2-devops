FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
RUN useradd -m -u 1001 apiuser
WORKDIR /app
COPY --from=builder /root/.local /home/apiuser/.local
COPY --chown=apiuser:apiuser . .
USER apiuser
ENV PATH=/home/apiuser/.local/bin:$PATH
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
