import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required  # Add this import
from django.conf import settings
import os

api_key = settings.API_KEY
read_access_token = settings.READ_ACCESS_TOKEN

def index(request):
    search_term = request.GET.get('search', '')  # Default to an empty string if no search term
    api_url = "https://api.themoviedb.org/3/movie/popular"  # Change to the endpoint you're using (e.g., for popular movies)

    # If there's a search term, modify the URL to search the API
    if search_term:
        api_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': settings.API_KEY,  # Your API key
            'query': search_term
        }
    else:
        params = {'api_key': settings.API_KEY}

    # Make the API request
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        movie_data = response.json().get('results', [])  # Fetch movies from the API
    else:
        movie_data = []  # Fallback if the API request fails

    # Save the movies into the database
    for movie in movie_data:
        movie_obj, created = Movie.objects.get_or_create(
            id=movie['id'],
            defaults={
                'name': movie['title'],
                'description': movie.get('overview', ''),
                'price': 9.99,  # Example price
                'image': movie.get('poster_path', ''),
            }
        )

    return render(request, 'movies/index.html', {'movies': movie_data})


# Show details of a single movie along with reviews
def show(request, id):
    # Fetch the movie and its reviews
    movie = get_object_or_404(Movie, id=id)
    reviews = Review.objects.filter(movie=movie)

    # Pass the movie and reviews directly to the template (no need for template_data)
    return render(request, 'movies/show.html', {'movie': movie, 'reviews': reviews})


# Create a review for a movie
@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = get_object_or_404(Movie, id=id)  # Fetch the movie
        review = Review(comment=request.POST['comment'], movie=movie, user=request.user)
        review.save()  # Save the review to the database
        return redirect('movies.show', id=id)  # Redirect back to the movie's show page
    return redirect('movies.show', id=id)  # Redirect if no comment is submitted


# Edit a review for a movie
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)  # Ensure only the review's owner can edit it
    
    if request.method == 'GET':
        return render(request, 'movies/edit_review.html', {'review': review})  # Show the edit form
    elif request.method == 'POST' and request.POST['comment'] != '':
        review.comment = request.POST['comment']  # Update the review comment
        review.save()  # Save the updated review
        return redirect('movies.show', id=id)  # Redirect back to the movie's show page
    return redirect('movies.show', id=id)  # Redirect if the comment is empty


# Delete a review for a movie
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()  # Delete the review
    return redirect('movies.show', id=id)  # Redirect back to the movie's show page
