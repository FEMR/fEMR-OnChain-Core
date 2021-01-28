#!/bin/bash

# Template Setup Script

export DEBUG=True
export SECRET_KEY=$(tr </dev/urandom -dc 'A-Za-z0-9!"#$%&'\''()*+,-./:;<=>?@[\]^_`{|}~' | head -c 50)
export QLDB_ENABLED="FALSE"  # Toggles QLDB on or off.
export qldb_name=""
export ADMIN_NAME=""
export ADMIN_EMAIL=""
export EMAIL_HOST=""
export EMAIL_PORT=""
export EMAIL_USERNAME=""
export EMAIL_PASSWORD=""
export DEFAULT_FROM_EMAIL=""
export SERVER_EMAIL=""

function all() {
  pip3 install -r requirements.txt
  python3 -m safety check -r requirements.txt
  python3 manage.py check
  migrate
  static
  run_tests
  pushd ./main/static/main/js
  npm install
  popd
  static
}

function run_tests() {
  python3 manage.py test main.tests
}

function clean() {
  rm -rf main/migrations/*
  files=$(find . -name "__pycache__")
  files2=$(find . -iregex ".*\.\(pyc\)")
  rm -rf ${files2}
  rm -rf ${files}
}

function migrate() {
  pwd
  python3 manage.py makemigrations main
  python3 manage.py makemigrations
  python3 manage.py migrate
}

function makemigrations() {
  python3 manage.py makemigrations main
  python3 manage.py makemigrations
}

function static() {
  python3 manage.py collectstatic
}

function run() {
  python3 manage.py runserver 0.0.0.0:8081
}

function reset_migrations() {
  python3 manage.py migrate --fake main
  python3 manage.py showmigrations
  rm -rf main/migrations
  python3 manage.py migrate --fake-initial
  python3 manage.py showmigrations
}

function createsuperuser() {
  python3 manage.py createsuperuser
}

function setup() {
  python3 manage.py creategroups
  python3 manage.py createadmin
}

function shell() {
  python3 manage.py shell
}

case "$1" in

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

all-run)
  all
  run
  ;;

all)
  all
  ;;

setup)
  all
  setup
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
