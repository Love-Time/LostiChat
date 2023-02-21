<h1 align="center">LOSTICHAT Django 4</h1>

## Project in development

## The frontend is https://github.com/ladiick/losti-chat
#### Install latest redis for windows https://github.com/tporadowski/redis/releases
## Start
    pip install -r req.txt
    uvicorn config.asgi:application
    celery -A config worker -l info -P gevent (Windows)

    celery -A config worker -l info  (Linux) and in config.cettings.py change REDIS_HOST

    

## API Routes

    POST /api/v1/auth/users/ - Registration with email
    POST /api/v1/token/ - Authorization with JWT Token
    POST /api/v1/token/refresh/ - updating the access token if it has died
    GET  /api/v1/auth/users/me/ - personal information

    GET /api/v1/auth/users/check_mail/?email=email Check mail exists with registration


    GET /api/v1/dialogs/ - Get list of dialogs
    GET /api/v1/findPeople/ Get list of people

    GET /api/v1/dialog/<int:pk>/ - Get all messages with the interlocutor with id <int:pk>
    POST /api/v1/dialog/message/ Send Message (message->str, recipient->int)

## WebSocket
    connect - /ws/chat/?token=[Your JWT Token]
### actions
    create_dialog_message (message->str, recipient->int, request_id=new Date.getTime())
   
    
## Admin

    admin/
    username: admin@mail.ru
    password: admin

    
    




