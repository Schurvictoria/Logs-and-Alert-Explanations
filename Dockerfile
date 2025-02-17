FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Optional envs
ENV OPENAI_API_KEY="" \
    EMAIL_HOST="" \
    EMAIL_PORT=587 \
    EMAIL_USER="" \
    EMAIL_PASSWORD="" \
    EMAIL_FROM="log-anomaly@example.com"

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
 CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

