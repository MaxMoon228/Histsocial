FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev cron && rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements
RUN pip install --no-cache-dir -r requirements/prod.txt
COPY . .
RUN chmod +x docker/scheduler/run_scheduler.sh

CMD ["sh", "docker/scheduler/run_scheduler.sh"]
