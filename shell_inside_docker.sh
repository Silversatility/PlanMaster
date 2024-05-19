#!/bin/bash
ENV_FILE="src/backend/env/settings.env"

[ ! -f $ENV_FILE ] &&
    echo "ERROR: Config file $ENV_FILE missing! Aborting" &&
    exit 1

# Get's docker up in detached mode (only if it isn't running)
docker-compose up -d >/dev/null 2>&1 &

# If no arguments as if you want a django or a bash shell
if [ "$#" -eq 0 ]; then
    read -n1 -p'Do you want a [b]ash or a [d]jango shell? Press Ctrl+C to cancel: ' res ; echo ""

    if [[ "$res" == "b" ]]; then
        echo "Starting bash shell..."
        docker-compose exec web bash -c "cd src/backend; bash"
        exit $?

    elif [[ "$res" == "d" ]]; then
        echo "Starting django shell..."
        docker-compose exec web bash -c "src/backend/manage.py shell -i ipython"
        exit $?

    else
        echo "Invalid answer. Exiting"
        exit 1
    fi

else
    # If arguments passed its definitely a bash shell what you need
    cmd="cd src/backend; $@"
    docker-compose exec $PRESET_FOR_INSTANCE_IF_EXISTS web bash -c "$cmd"
    exit $?
fi
