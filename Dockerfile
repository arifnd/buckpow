FROM python:3.12-slim

WORKDIR /code

COPY requirements-prod.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
    adduser --disabled-password --gecos '' appuser

COPY alembic.ini /code/alembic.ini
COPY ./migrations /code/migrations
COPY ./app /code/app

RUN mkdir -p /code/instance && chown -R appuser:appuser /code

USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--proxy-headers"]
