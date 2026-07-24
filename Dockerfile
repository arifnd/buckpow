# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir --upgrade -r /app/requirements/prod.txt && \
    adduser --disabled-password --gecos '' appuser

COPY .env.example /app/.env
COPY alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations
COPY ./src /app/src
COPY ./templates /app/templates

RUN mkdir -p /app/instance && chown -R appuser:appuser /app
COPY --chmod=755 ./scripts /app/scripts

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/scripts/start.sh"]
