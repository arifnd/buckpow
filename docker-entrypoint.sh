#!/bin/sh
set -e

flask init-db

exec gunicorn run:app -w 4 -b 0.0.0.0:5000
