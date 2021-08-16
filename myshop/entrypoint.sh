#!/usr/bin/env sh

python manage.py migrate

gunicorn myshop.wsgi:application --bind 0.0.0.0:8000 --reload -w 4