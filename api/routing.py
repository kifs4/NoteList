from django.urls import re_path
from typing import Any
from . import consumers

# Явно вказуємо тип для лінтера, якщо він продовжує підсвічувати
websocket_urlpatterns: list[Any] = [
    re_path(r'ws/app/$', consumers.NoteListConsumer.as_asgi()),
]