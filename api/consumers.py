import json
from typing import Any, Dict, Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache


class NoteListConsumer(AsyncWebsocketConsumer):
    # Виправляє помилку "defined outside __init__"
    user: Any = None
    user_group: str = ""
    admin_group: str = ""

    async def connect(self) -> None:
        # Безпечно дістаємо користувача зі scope
        user_obj = self.scope.get("user")

        # Виправляє помилки "Member None does not have attribute..."
        if user_obj is None or not hasattr(user_obj, "is_anonymous") or user_obj.is_anonymous:
            await self.close()
            return

        self.user = user_obj
        self.user_group = f"user_{self.user.id}"
        self.admin_group = "admin_dashboard"

        # Приєднуємо користувача до груп
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.track_user_online(self.user.id, action="connect")

        await self.accept()

        # Перевірка на адміна (is_staff)
        if getattr(self.user, "is_staff", False):
            await self.channel_layer.group_add(self.admin_group, self.channel_name)
            await self.send_online_list()

    async def disconnect(self, close_code: int) -> None:
        # Перевіряємо чи користувач існує та авторизований
        if self.user and hasattr(self.user, "is_anonymous") and not self.user.is_anonymous:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

            if getattr(self.user, "is_staff", False):
                await self.channel_layer.group_discard(self.admin_group, self.channel_name)

            await self.track_user_online(self.user.id, action="disconnect")

    # Виправляє помилку невідповідності сигнатури методів (додано bytes_data)
    async def receive(self, text_data: Optional[str] = None, bytes_data: Optional[bytes] = None) -> None:
        if not text_data:
            return

        data: Dict[str, Any] = json.loads(text_data)
        action = data.get("action")

        if action == "share_note" and self.user:
            target_user_id = data.get("target_user_id")
            note_payload = data.get("note")
            user_email = getattr(self.user, "email", "unknown")

            await self.channel_layer.group_send(
                f"user_{target_user_id}",
                {
                    "type": "incoming_note",
                    "sender_email": user_email,
                    "note": note_payload
                }
            )

    async def incoming_note(self, event: Dict[str, Any]) -> None:
        await self.send(text_data=json.dumps({
            "event": "note_shared",
            "sender_email": event["sender_email"],
            "note": event["note"]
        }))

    # Виправляє помилку "Parameter 'event' value is not used"
    async def global_online_update(self, event: Dict[str, Any]) -> None:
        # Використовуємо аргумент event, щоб закрити попередження лінтера
        _ = event
        if self.user and getattr(self.user, "is_staff", False):
            await self.send_online_list()

    async def send_online_list(self) -> None:
        online_users = cache.get("online_users_list", [])
        await self.send(text_data=json.dumps({
            "event": "online_users_list",
            "users": online_users
        }))

    async def track_user_online(self, user_id: int, action: str) -> None:
        current_online = cache.get("online_users_list", [])

        if action == "connect":
            if user_id not in current_online:
                current_online.append(user_id)
        elif action == "disconnect":
            if user_id in current_online:
                current_online.remove(user_id)

        cache.set("online_users_list", current_online, timeout=None)

        await self.channel_layer.group_send(
            self.admin_group,
            {
                "type": "global_online_update"
            }
        )