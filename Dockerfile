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

USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "src/main.py", "--port", "8000", "--proxy-headers"]
