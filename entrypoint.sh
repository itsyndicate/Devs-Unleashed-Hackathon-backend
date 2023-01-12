#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

pip install -r requirements.txt
python manage.py migrate --noinput

if [ "$MODE" = "PRODUCTION" ] || [ "$MODE" = "STAGING" ]
then
  python manage.py collectstatic --noinput
  daphne -b 0.0.0.0 -p 8000 taskogotchi.asgi:application
fi

exec "$@"
