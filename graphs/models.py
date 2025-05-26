from django.db import models
from django.conf import settings
import json
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('registered', 'Registered'),
        ('guest', 'Guest'),
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='registered'
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Graph(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    data = models.JSONField()  # Будет хранить данные для столбчатой диаграммы
    created_at = models.DateTimeField(auto_now_add=True)

    def get_data(self):
        return self.data