FROM python:3.12-slim

WORKDIR /code

COPY requirements-prod.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY alembic.ini /code/alembic.ini
COPY ./migrations /code/migrations
COPY ./app /code/app

EXPOSE 5000

CMD ["fastapi", "run", "app/main.py", "--port", "5000", "--proxy-headers"]
