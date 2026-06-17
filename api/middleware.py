from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    try:
        # Використовуємо рідний клас SimpleJWT, який сам знає правильний SECRET_KEY та алгоритм
        access_token = AccessToken(token_string)
        user_id = access_token['user_id']  # Дістаємо id користувача з payload
        return User.objects.get(id=user_id)
    except Exception:
        # Якщо токен прострочений або підпис невірний — повертаємо аноніма
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, send, receive):
        headers = dict(scope.get("headers", []))

        # Дістаємо заголовок authorization (в нижньому регістрі)
        auth_header = headers.get(b"authorization", b"").decode("utf-8")

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, send, receive)