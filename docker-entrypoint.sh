#!/bin/sh
set -e

flask init-db

exec gunicorn run:app -w ${GUNICORN_WORKERS:-4} -b 0.0.0.0:5000
