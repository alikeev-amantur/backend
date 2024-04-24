#!/bin/bash

python production-manage.py migrate --noinput

python production-manage.py collectstatic --noinput



gunicorn --workers=3 --bind 0.0.0.0:8000
