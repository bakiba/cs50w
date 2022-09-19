# CS50w final Capstone project

This is my final project for CS50w course. Client Photo Gallery is web application for photographers to share their work with clients who will be able to select and comment on images they want for final processing.

Web application is build using Django which is packed into docker containers running gunicorn and nginx.

## How to run
* clone this repo
* create `.env` file in the root folder of repo and define following environment variables (ensue .env has unix line endings):
        
        DEBUG=1
        DJANGO_SECRET_KEY='some string of random characters'
        DJANGO_ALLOWED_HOSTS='localhost 127.0.0.1 [::1] *'

* if you want to deploy to docker containers, ensure docker is installed and run:

       sudo docker-compose up -d --build

* if you want to run standalone Django, ensure you have python 3.x installed and run following:

       python3 -m venv env
       . env/bin/activate
       pip install --upgrade pip
       pip install django
       set -a && source .env && set +a
       python capstone/manage.py runserver 0.0.0.0:5000

      

