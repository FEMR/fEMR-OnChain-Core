#!/bin/bash
set -e
source /var/app/venv/*/bin/activate
cd /var/app/staging

python manage.py makemigrations main
python manage.py makemigrations app_mr
python manage.py makemigrations clinic_messages
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py creategroups
python manage.py createadmin
python manage.py adminoptions
python manage.py createinventoryforms
python manage.py createraceandethnicity
