from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)  # Birthdate field

    def __str__(self):
        return self.user.username
