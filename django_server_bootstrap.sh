#!/bin/bash
APP_DIR="/code/src/backend"
APPS=account construction
ENV_FILE="/code/src/backend/env/settings.env"

cd $APP_DIR
while true; do
    [ ! -f $ENV_FILE ] &&
        echo "ERROR: Config file $ENV_FILE missing! Django will not start" &&
        sleep 10 &&
        continue

    echo -e "\ndocker_bootstrap here: waiting for DB to be ready..." && sleep 3

    pip install -r requirements.txt
    python3 manage.py makemigrations ${APPS}
    python3 manage.py migrate

    if [ -z "$PRODUCTION_SERVER" ]; then
        echo -e "\n(*) DEVELOPMENT_MODE: Starting runserver..."
        python3 manage.py runserver 0.0.0.0:9000
        echo -e "\n(!) Server exited with RC=$?. Restarting..."
    else
        echo -e "\n(*) PRODUCTION_MODE: Starting gunicorn..."
        gunicorn --bind 0.0.0.0:9000 outplacement.wsgi:application
        echo -e "\n(!) Server exited with RC=$?. Restarting..."
    fi
done
