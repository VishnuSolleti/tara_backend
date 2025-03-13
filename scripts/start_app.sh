#!/usr/bin/bash

python manage.py migrate
python manage.py makemigrations
python manage.py collectstatic
sudo service gunicorn restart
sudo service nginx restart
echo process done
