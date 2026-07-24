#!/bin/sh
set -e

alembic upgrade head

exec fastapi run src/main.py --port 8000 --proxy-headers
