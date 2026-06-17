from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Task
from .serializers import RegisterSerializer, UserProfileSerializer, TaskSerializer

# 1. Реєстрація
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# 2. Профіль користувача (Перегляд та редагування)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# 3. Про додаток (Статичний опис)
class AboutAppView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "app_name": "To-Do List API",
            "version": "1.0.0",
            "description": "Це зручний REST API додаток для керування щоденними завданнями. "
                           "Він дозволяє реєструватися, авторизуватися та повністю контролювати свій список справ."
        }, status=status.HTTP_200_OK)

# 4. Робочі функції (CRUD для завдань)
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Користувач бачить тільки власні завдання
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Автоматично прив'язуємо завдання до поточного користувача
        serializer.save(user=self.request.user)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)