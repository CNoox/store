#!/bin/sh

exec gunicorn shop.wsgi:application --bind 0.0.0.0:8000