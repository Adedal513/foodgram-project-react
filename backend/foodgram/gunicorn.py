# WSGI App

wsgi_app = 'foodgram.wsgi:application'

# User and Group


# Workers

workers = 1
worker_class = 'sync'
threads = 16

# Server socket

bind = '0.0.0.0:8000'
backlog = 2048

# Logging

loglevel = 'info'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'

# Daemon

daemon = False
