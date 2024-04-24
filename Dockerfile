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


RUN if [ "$ENVIRONMENT" = "production" ]; then python manage.py collectstatic --noinput; fi

CMD if [ "$ENVIRONMENT" = "production" ] ; then gunicorn --workers=3 --bind 0.0.0.0:8000 happyhours.wsgi:application; else python manage.py runserver 0.0.0.0:8000; fi