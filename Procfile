web: gunicorn sush.wsgi:application --log-file - --log-level debug
python manage.py collectstatic --noinput
py manage.py migrate