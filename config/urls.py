from django.contrib import admin
from django.urls import path, include
# Імпортуємо вбудовані представлення від drf-spectacular
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # маршрути вашого додатка NoteList

    # 1. За цим посиланням генеруватиметься сирий JSON/YAML файл специфікації
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # 2. Інтерактивна документація REDOC (Те, що потрібно для звіту)
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # 3. (Опціонально) Альтернативний інтерфейс Swagger UI
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]