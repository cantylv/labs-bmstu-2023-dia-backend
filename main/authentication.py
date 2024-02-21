from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from .models import CustomUser
import redis

session_storage = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class RedisSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        session_id = request.COOKIES.get('session_id')

        if session_id is None:
            return AnonymousUser, None
        else:
            try:
                user_id = session_storage.get(session_id)
                if user_id is None:
                    return AnonymousUser, None
                user_id = int(user_id)
                user = CustomUser.objects.get(pk=user_id)
                # Возвращение кортежа (пользователь, данные аутентификации), если аутентификация прошла успешно
                return user, True
            except CustomUser.DoesNotExist:
                return AnonymousUser, None