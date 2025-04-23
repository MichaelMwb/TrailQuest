from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)  # Birthdate field

    def __str__(self):
        return self.user.username

class TripPreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link trip preferences to a user
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
    itinerary = models.TextField(null=True, blank=True)  # Add this field to store the itinerary JSON

    def __str__(self):
        return self.trip_name

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link trip to a user
    trip_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)  # Optional date field
    group_size = models.PositiveIntegerField()
    activity = models.CharField(max_length=100)
    duration = models.PositiveIntegerField()  # Duration in days
    difficulty = models.CharField(max_length=50)
    itinerary = models.TextField(null=True, blank=True)  # Store the itinerary JSON
    completed = models.BooleanField(default=False)  # Mark if the trip is completed
    visible_in_saved = models.BooleanField(default=True)

    def __str__(self):
        return f"Trip - {self.location} ({'Completed' if self.completed else 'Current'})"
