from django.db import models
from django.conf import settings
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile
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

def graph_image_path(instance, filename):
    return f'graphs/user_{instance.user.id}/{filename}'

class Graph(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    data = models.JSONField()  # Будет хранить данные для столбчатой диаграммы
    graph_image = models.ImageField(upload_to='graphs/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.generate_graph()
        super().save(*args, **kwargs)

    def generate_graph(self):
        plt.switch_backend('Agg')

        # Получаем данные из JSON
        data = self.data
        labels = list(data.keys())
        values = list(data.values())

        plt.figure(figsize=(8, 6))
        plt.bar(labels, values)
        plt.title(f'Столбчатая диаграмма: {self.title}')
        plt.xlabel('Категории')
        plt.ylabel('Значения')
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        plt.close()

        filename = f'graph_{self.title}_{self.id}.png'
        self.graph_image.save(filename, ContentFile(buffer.getvalue()), save=False)

    def get_data(self):
        return self.data