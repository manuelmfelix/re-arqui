source venv/bin/activate
gunicorn re_arqui.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=re_arqui.settings_prod