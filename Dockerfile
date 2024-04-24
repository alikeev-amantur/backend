FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /code

RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .


CMD if [ "$ENVIRONMENT" = "production" ] ; python production-manage.py migrate --noinput && \
    python production-manage.py collectstatic --noinput  && \
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); email='$SUPERUSER_EMAIL'; password='$SUPERUSER_PASSWORD'; user=User.objects.filter(email=email).first(); if not user: User.objects.create_superuser(email=email, password=password);" | python production-manage.py shell && \
    gunicorn --workers=3 --bind 0.0.0.0:8000 happyhours.wsgi:application;\
    else python manage.py runserver 0.0.0.0:8000; fi