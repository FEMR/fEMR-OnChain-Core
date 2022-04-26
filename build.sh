#!/bin/bash

export DEBUG=$DEBUG
export SECRET_KEY=$SECRET_KEY
export QLDB_ENABLED=$QLDB_ENABLED
export qldb_name=$qldb_name
export ADMIN_NAME=$ADMIN_NAME
export ADMIN_EMAIL=$ADMIN_EMAIL
export EMAIL_HOST=$EMAIL_HOST
export EMAIL_PORT=$EMAIL_PORT
export EMAIL_USERNAME=$EMAIL_USERNAME
export EMAIL_PASSWORD=$EMAIL_PASSWORD
export DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL
export SERVER_EMAIL=$SERVER_EMAIL
export ENVIRONMENT=$ENVIRONMENT

function all() {
  migrate
  pip3 install -r requirements.txt
  static
  pushd ./main/static/main/js || exit
  npm install
  popd || exit
  static
}

function run_tests() {
  python3 manage.py test
}

function clean() {
  rm -rf main/migrations/*
  files=$(find . -name "__pycache__")
  files2=$(find . -iregex ".*\.\(pyc\)")
  rm -rf "${files2}"
  rm -rf "${files}"
}

function migrate() {
  pwd
  python3 manage.py makemigrations main
  python3 manage.py makemigrations app_mr
  python3 manage.py makemigrations clinic_messages
  python3 manage.py makemigrations
  python3 manage.py migrate
}

function makemigrations() {
  python3 manage.py makemigrations main
  python3 manage.py makemigrations app_mr
  python3 manage.py makemigrations clinic_messages
  python3 manage.py makemigrations
}

function static() {
  python3 manage.py collectstatic --no-input
}

function run() {
  python3 manage.py runserver 0.0.0.0:8081
}

function documents() {
  rm -rf build/
  sphinx-apidoc -f -o source main
  sphinx-apidoc -f -o source app_mr
  sphinx-apidoc -f -o source clinic_messages
  make html
  mkdir -p docs/
  cp -rf build/html/* docs/
}

function reset_migrations() {
  python3 manage.py migrate --fake main
  python3 manage.py showmigrations
  rm -rf main/migrations
  python3 manage.py migrate --fake-initial
  python3 manage.py showmigrations
}

function setup() {
  python3 manage.py creategroups
  python3 manage.py createadmin
  python3 manage.py adminoptions
  python3 manage.py createinventoryforms
  python3 manage.py createraceandethnicity
}

function docker-setup() {
  python3 manage.py scaledata
}

function createsuperuser() {
  python3 manage.py createsuperuser
}

function shell() {
  python3 manage.py shell
}

function check() {
  # We're going to ignore E1101, since Django exposes members to Model classes
  # that PyLint can't see.
  clear && \
   black . && \
   run_tests && \
   pylint main app_mr clinic_messages --disable=E1101,W0613,R0903,C0301,C0114,C0115,C0116,R0801
}

function celery() {
  celery --app=femr_onchain worker
}

function gunicorn_run() {
  gunicorn femr_onchain.wsgi:application --bind 0.0.0.0:8081
}

case "$1" in

celery)
  celery
  ;;

check)
  check
  ;;

doc)
  documents
  ;;

startapp)
  python3 manage.py startapp "$2"
  ;;

clean)
  clean
  ;;

migrate)
  migrate
  ;;

test)
  run_tests
  ;;

run)
  run
  ;;

setup)
  setup
  ;;

init-all-run)
  all
  setup
  gunicorn_run
  ;;

docker-init-all)
  check
  all
  setup
  docker-setup
  all
  ;;

all-run)
  check
  all
  run
  ;;

all)
  all
  ;;

reset_migrations)
  reset_migrations
  ;;

makemigrations)
  makemigrations
  ;;

createsuperuser)
  createsuperuser
  ;;

shell)
  shell
  ;;

esac
