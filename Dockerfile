# Production image for the AIO audit web app.
# Build context = repo root:  docker build -t aio-audit .
FROM python:3.12-slim

WORKDIR /app
COPY experiments/ /app/experiments/

RUN pip install --no-cache-dir -r /app/experiments/requirements.txt gunicorn \
    && mkdir -p /app/workspace/geo-audits /app/experiments/results

WORKDIR /app/experiments
EXPOSE 8000

# IMPORTANT: a single worker — the job registry and progress live in memory,
# so multiple workers would not see each other's jobs. Threads give concurrency.
CMD ["gunicorn", "-w", "1", "--threads", "8", "-b", "0.0.0.0:8000", \
     "--timeout", "180", "webapp:app"]
