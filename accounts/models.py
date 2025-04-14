from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)  # Birthdate field

    def __str__(self):
        return self.user.username

class TripPreferences(models.Model):
    location = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField()
    
    ACTIVITY_CHOICES = [
        ('hiking', 'Hiking'),
        ('camping', 'Camping'),
        ('both', 'Both'),
    ]
    activities = models.CharField(max_length=10, choices=ACTIVITY_CHOICES)
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    
    group_size = models.PositiveIntegerField()
    trip_name = models.CharField(max_length=100)

    def __str__(self):
        return self.trip_name
