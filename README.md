<h2 align="center">LOSTICHAT на Django 4</h2>

###

## The frontend is https://github.com/ladiick/losti-chat
## Старт
    pip install -r req.txt
    python manage.py runserver

## API Маршруты
   api/v1/auth/users/ - [POST] - Registration with email
   api/v1/token/ - [POST] Authorization with JWT Token
   api/v1/token/refresh/ [POST] updating the access token if it has died
   api/v1/auth/users/me/ [GET]Information about me
   
    
## Admin

    admin/
    username: admin
    password: admin

    
    




