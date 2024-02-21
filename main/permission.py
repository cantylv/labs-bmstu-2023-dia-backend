from rest_framework import permissions
from django.contrib.sessions.models import Session
from main.models import CustomUser

import redis
from django.conf import settings

session_storage = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        session_key = request.COOKIES.get('session_id', None)
        if session_key is None:
            return False
        try:
            user_id = int(session_storage.get(session_key))
            user = CustomUser.objects.get(pk=user_id)
            if user.is_superuser:
                return True
            return False
        except Session.DoesNotExist:
            return False


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        session_key = request.COOKIES.get('session_id', None)
        if session_key is None:
            return False
        try:
            user_id = int(session_storage.get(session_key))
            user = CustomUser.objects.get(pk=user_id)
            if user.is_staff or user.is_superuser:
                return False
            return True
        except Session.DoesNotExist:
            return False


class IsAnonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        session_key = request.COOKIES.get('session_id', None)
        if session_key is None:
            return True
        else:
            return False


class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        access_token = request.COOKIES.get("session_id", None)
        if access_token:
            return True
        else:
            return False