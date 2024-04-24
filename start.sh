#!/bin/bash

python production-manage.py migrate --noinput

python production-manage.py collectstatic --noinput

echo "from django.contrib.auth import get_user_model; User = get_user_model();  email='$SUPERUSER_EMAIL'; password='$SUPERUSER_PASSWORD'; user=User.objects.filter(email=email).first(); if not user: User.objects.create_superuser(email, password); " | python production-manage.py shell

gunicorn --workers=3 --bind 0.0.0.0:8000
