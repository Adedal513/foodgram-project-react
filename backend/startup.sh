#!/bin/bash

# Running migrations
python manage.py migrate
# Collecting static files
python manage.py collectstatic --noinput
# Starting WSGI server
gunicorn -c foodgram/gunicorn.py