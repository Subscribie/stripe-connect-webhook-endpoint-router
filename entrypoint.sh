#! /bin/bash
set -euxo pipefail

export FLASK_APP=main.py
export FLASK_DEBUG=1

exec uwsgi --http :80 --workers 1 --chdir /usr/src/app/ --mount /=main:app

