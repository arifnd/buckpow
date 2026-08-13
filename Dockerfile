FROM astral/uv:python3.12-trixie-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml

FROM python:3.12-slim-trixie AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY .env.example /app/.env
COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations
COPY src /app/src
COPY templates /app/templates
COPY static /app/static

RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/instance && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && exec fastapi run src/main.py --port 8000 --proxy-headers"]
