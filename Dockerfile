FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

RUN mkdir -p instance

ENV GUNICORN_WORKERS=4

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]
