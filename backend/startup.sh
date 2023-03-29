#!/bin/bash

# Running migrations
python manage.py migrate
# Collecting static files
python manage.py collectstatic --noinput
# Populating database with initial data
python manage.py load_db
# Starting WSGI server
gunicorn -c foodgram/gunicorn.py