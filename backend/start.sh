#!/bin/sh

celery -A shop worker --loglevel=info &

celery -A shop beat --loglevel=info &

exec gunicorn shop.wsgi:application --bind 0.0.0.0:8000