FROM python:3.10.7-slim

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DJANGO_SETTINGS_MODULE 'foodgram.settings'

RUN apt-get update && apt-get install -y netcat
COPY requirements.txt requirements.txt

RUN apt -y install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 \
    && mkdir -p /var/www/static/ \
    && mkdir -p /var/www/media/ \
    && mkdir /var/log/gunicorn \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
