<h2 align="center">LOSTICHAT на Django 4</h2>

###

## The frontend is https://github.com/ladiick/losti-chat
## Старт
    pip install -r req.txt
    python manage.py runserver

## API Маршруты

    POST /api/v1/auth/users/ - Registration with email
    POST /api/v1/token/ - Authorization with JWT Token
    POST /api/v1/token/refresh/ - updating the access token if it has died
    GET  /api/v1/auth/users/me/ - personal information 

    GET /api/v1/dialogs/ - Get list of dialogs


   
    
## Admin

    admin/
    username: admin
    password: admin

    
    




