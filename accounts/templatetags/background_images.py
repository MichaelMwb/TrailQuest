import os
from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def get_background_images():
    background_folder = os.path.join(settings.STATICFILES_DIRS[0], 'background')
    print("Background folder path:", background_folder)  # Debug: Log the folder path

    # Check if the folder exists
    if not os.path.exists(background_folder):
        print("Background folder does not exist!")
        return []

    # Log the contents of the folder
    print("Contents of background folder:", os.listdir(background_folder))

    # Filter and return images
    images = [f for f in os.listdir(background_folder) if f.endswith(('.jpg', '.jpeg'))]
    print("Images found:", images)  # Debug: Log the images
    return sorted(images, key=lambda x: int(os.path.splitext(x)[0]))