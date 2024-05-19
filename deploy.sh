#!/bin/bash

source ~/.virtualenvs/crewboss/bin/activate
cd ~/crewboss_web/src/backend/
pip install -r requirements.txt
python manage.py makemigrations account construction
python manage.py migrate
sudo service daphne restart
deactivate

cd ~/crewboss_web/src/frontend/
npm install
./node_modules/@vue/cli-service/bin/vue-cli-service.js build --mode production

cd ~/crewboss_web/
