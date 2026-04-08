web: gunicorn --workers=2 --threads=5 --max-requests 5 femr_onchain.wsgi:application --bind 0.0.0.0:8000
worker: celery -A femr_onchain worker --loglevel=info
beat: celery -A femr_onchain beat --loglevel=info
