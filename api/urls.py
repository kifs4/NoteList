from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, AboutAppView, TaskListCreateView, TaskDetailView

urlpatterns = [
    # Автентифікація
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Профіль та Інфо
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('about/', AboutAppView.as_view(), name='about_app'),

    # Завдання (To-Do)
    path('tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
]