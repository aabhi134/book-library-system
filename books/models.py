from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):

    STATUS_CHOICES = [
        ('to_read', 'To Read'),
        ('reading', 'Reading'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='books'
    )

    title = models.CharField(max_length=200)

    author = models.CharField(max_length=200)

    genre = models.CharField(max_length=100)

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='to_read'
    )

    ai_summary = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title