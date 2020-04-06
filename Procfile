release: python manage.py migrate --noinput
web: gunicorn watchdog_django_project.wsgi
worker: python watchdog_worker.py
