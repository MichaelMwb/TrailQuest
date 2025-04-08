from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/', blank=True, null=True, default='default-movie.png')

    def get_image_url(self):
        """Return the image URL or default if not available."""
        if self.image:
            return self.image.url
        return os.path.join(settings.STATIC_URL, 'img/default-movie.png')

    def __str__(self):
        return f"{self.id} - {self.name}"

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.movie.name}"