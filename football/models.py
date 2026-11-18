from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to="profiles/")
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=100)
    players_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class Field(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="fields")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField()
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookings")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="bookings")
    has_team = models.BooleanField()
    players_needed = models.PositiveIntegerField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class Participant(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)