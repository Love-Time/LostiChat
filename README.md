<h1 align="center">LOSTICHAT Django 4</h1>

## Project in development

## The frontend is https://github.com/ladiick/losti-chat
#### Install latest redis for windows https://github.com/tporadowski/redis/releases
## Start
    pip install -r req.txt
    uvicorn config.asgi:application
    celery -A config worker -l info -P gevent (Windows)

    celery -A config worker -l info  (Linux) and in config.cettings.py change REDIS_HOST

    celery -A config beat (not necessary, for clearing database codeModel every 2 hours)

## Start with docker-compose
    - clone 2 projects into one folder
    - rename losti-chat to frontend
    - docker-compose up


    

## Swagger
    /swagger/

    
    connect - /ws/chat/?token=[Your JWT Token]
### actions
    create_dialog_message (message->str, recipient->int, request_id=new Date.getTime())
   
    
## Admin

    admin/
    username: admin@mail.ru
    password: admin

    
    




