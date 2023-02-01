import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from django.http import HttpResponse
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response

from config import settings
User = get_user_model()

class BadRequest:
    def __init__(self, get_response):
        self._get_response = get_response
    def __call__(self, request):
        response = self._get_response(request)
        response['Access-Control-Allow-Headers'] = "*"
        response['Access-Control-Allow-Methods'] = "*"
        response['Access-Control-Allow-Origin'] = "*"
        return response

    # def process_exception(self, request, exception):
    #     print(f'Exception:  {exception}')
    #     return HttpResponse(f"Бекенд не говно, идите нахуй. {exception}", status=status.HTTP_400_BAD_REQUEST)




ALGORITHM = "HS256"
@database_sync_to_async
def get_user(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        print('payload', payload)
    except:
        print('no payload')
        return AnonymousUser()

    token_exp = datetime.fromtimestamp(payload['exp'])
    if token_exp < datetime.utcnow():
        print("no date-time")
        return AnonymousUser()

    try:
        user = User.objects.get(id=payload['user_id'])
        print('user', user)
    except User.DoesNotExist:
        print('no user')
        return AnonymousUser()

    return user

class TokenAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        close_old_connections()
        # token_key = scope['query_string'].decode().split('=')[-1]
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None
        # try:
        #     token_key = dict(scope['headers'])[b'sec-websocket-protocol'].decode('utf-8')
        #     print('d1', token_key)
        # except ValueError:
        #     token_key = None

        scope['user'] = await get_user(token_key)
        print('d2', scope['user'])
        return await super().__call__(scope, receive, send)