import os
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    login as auth_login, authenticate, logout as auth_logout,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt  # Use csrf_protect in production
from django.views.decorators.http import require_POST

from .forms import (
    CustomUserCreationForm, CustomErrorList,
    ForgotPasswordForm, PasswordResetForm, TripPreferencesForm
)
from .models import UserProfile

from openai import OpenAI


@login_required
def logout(request):
    auth_logout(request)
    # Clear all messages
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # This iterates through the messages and clears them
    return redirect('accounts.login')

def login(request):
    # Redirect authenticated users to the trip preferences page
    if request.user.is_authenticated:
        return redirect('trip_preferences')  # Replace with the appropriate redirect URL

    template_data = {'title': 'Login'}
    if request.method == 'GET':
        return render(request, 'accounts/login.html', template_data)
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', template_data)
        else:
            auth_login(request, user)
            return redirect('trip_preferences')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    
    # Retrieve all orders for the logged-in user
    user_orders = request.user.order_set.all().order_by('id')

    # Add a user-specific order number instead of using the database ID
    for index, order in enumerate(user_orders, start=1):
        order.user_order_number = index  # Assign sequential numbers per user

    template_data['orders'] = user_orders
    return render(request, 'accounts/orders.html', {'template_data' : template_data})

def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            birthdate = form.cleaned_data["birthdate"]

            try:
                user = User.objects.get(username=username)
                profile = UserProfile.objects.get(user=user)

                if profile.birthdate == birthdate:
                    # Store user ID in session for password reset
                    request.session['reset_user_id'] = user.id
                    return redirect('accounts.reset_password')  # Redirect to reset password page
                else:
                    messages.error(request, "Incorrect birthdate.")
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                messages.error(request, "User not found.")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/forgot_password.html", {"form": form})

def reset_password(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        messages.error(request, "Your session has expired. Please try the forgot password process again.")
        return redirect("accounts.forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password1 = form.cleaned_data['new_password1']
            new_password2 = form.cleaned_data['new_password2']

            if new_password1 == new_password2:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)  # Keeps the user logged in
                messages.success(request, "Your password has been reset successfully.")
                del request.session['reset_user_id']  # Clear session
                return redirect("accounts.login")
            else:
                messages.error(request, "Passwords do not match.")
    else:
        form = PasswordResetForm()

    return render(request, "accounts/reset_password.html", {"form": form})

    from django.conf import settings
    from openai import OpenAI

@login_required
def trip_preferences_view(request):
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY
    )


    # Fetch images from the static/background/ folder
    background_folder = os.path.join(settings.STATICFILES_DIRS[0], 'background')
    images = [
        f"background/{file}" for file in os.listdir(background_folder)
        if file.endswith(('.jpg', '.jpeg'))
    ]

    if request.method == 'POST':
        form = TripPreferencesForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Delete any existing incomplete trips for the user
            Trip.objects.filter(user=request.user, completed=False).delete()

            # Construct the prompt
            prompt = f"""Create a detailed itinerary and packing checklist for a {cd['duration']}-day trip to {cd['location']}.
            Trip name: {cd['trip_name']}
            Activity type: {cd['activities']}
            Difficulty level: {cd['difficulty']}
            Group size: {cd['group_size']}
            
            For each day in the itinerary, please provide the main activities AND 2-3 alternative activity suggestions that match the activity type and difficulty.
            
            Please provide the response in the following JSON format:
            {{ 
                "name": "trip name",
                "location": "location name",
                "difficulty": "easy/medium/hard",
                "packing_checklist": {{
                    "essentials": ["item1", "item2", "item3"],
                    "clothing": ["item1", "item2", "item3"],
                    "gear": ["item1", "item2", "item3"],
                    "food_and_water": ["item1", "item2", "item3"],
                    "safety": ["item1", "item2", "item3"]
                }},
                "days": {{
                    "1": {{ 
                        "activities": [
                            {{
                                "name": "main activity name",
                                "location": "main activity location",
                                "description": "main activity description",
                                "duration": "duration in hours"
                            }}
                        ],
                        "suggestions": [
                            {{
                                "name": "suggestion name 1",
                                "location": "suggestion location 1",
                                "description": "suggestion description 1",
                                "duration": "suggestion duration 1"
                            }},
                            {{
                                "name": "suggestion name 2",
                                "location": "suggestion location 2",
                                "description": "suggestion description 2",
                                "duration": "suggestion duration 2"
                            }}
                        ]
                    }} 
                    // ... more days ...
                }}
            }}
            In the JSON response, make sure that all locations (both main activities and suggestions) are real places that can be queried by Google Maps, and I can get directions to. Ensure suggestions fit the activity type '{cd['activities']}' and difficulty '{cd['difficulty']}'.
            """

            # Call OpenAI API
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert trail and camping trip planner."},
                        {"role": "user", "content": prompt}
                    ],
                    timeout=30  # Increase timeout to 30 seconds
                )
            except Timeout as e:
                print("OpenAI API Timeout:", e)
                messages.error(request, "The request to the OpenAI API timed out. Please try again.")
                return redirect('trip_preferences')

            # Extract and clean the response content
            raw_content = response.choices[0].message.content

            # Improved cleaning logic
            if "```json" in raw_content:
                cleaned_content = raw_content.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_content:
                cleaned_content = raw_content.split("```")[1].split("```")[0].strip()
            else:
                cleaned_content = raw_content.strip()

            # Validate the cleaned content
            if not cleaned_content.startswith("{") or not cleaned_content.endswith("}"):
                messages.error(request, "The OpenAI API returned an invalid itinerary format. Please try again.")
                return redirect('trip_preferences')

            # Attempt to parse the cleaned content
            try:
                itinerary_data = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                messages.error(request, "Failed to parse the itinerary. Please try again.")
                return redirect('trip_preferences')

            for day in itinerary_data['days']:
                for i in range(len(itinerary_data['days'][day]['activities'])):
                    # Add a Google Maps link to the location
                    itinerary_data['days'][day]['activities'][i]['location'] = itinerary_data['days'][day]['activities'][i]['location'] + "|https://www.google.com/maps/search/?api=1&query=" + itinerary_data['days'][day]['activities'][i]['location'].lower().replace(" ", "+")

                for i in range(len(itinerary_data['days'][day]['suggestions'])):
                    # Add a Google Maps link to the location
                    itinerary_data['days'][day]['suggestions'][i]['location'] = itinerary_data['days'][day]['suggestions'][i]['location'] + "|https://www.google.com/maps/search/?api=1&query=" + itinerary_data['days'][day]['suggestions'][i]['location'].lower().replace(" ", "+")

            print("About to save the trip...")
            # Save the trip
            Trip.objects.create(
                user=request.user,
                trip_name=cd['trip_name'] if cd['trip_name'] else "Untitled Trip",
                location=cd['location'],
                group_size=cd['group_size'],
                activity=cd['activities'],
                duration=cd['duration'],
                difficulty=cd['difficulty'],
                itinerary=json.dumps(itinerary_data),  # Save the itinerary JSON
                completed=False  # Mark as not completed
            )

            return redirect('trip_suggestions')

    else:
        form = TripPreferencesForm()

    # Pass the images and form to the template
    return render(request, 'accounts/trip_preferences.html', {'form': form, 
                                                              'images_json': mark_safe(json.dumps(images)),  'images': images, 'google_places_key': settings.GOOGLE_PLACES_API_KEY})

from django.shortcuts import render
from .models import Trip
import json

@login_required
def past_trips(request):
    # Retrieve completed trips for the logged-in user, ordered by most recent first
    trips = Trip.objects.filter(user=request.user, completed=True).order_by('-id')

    # Deserialize the itinerary JSON for each trip
    for trip in trips:
        if trip.itinerary:
            try:
                trip.itinerary = json.loads(trip.itinerary)  # Convert JSON string to Python dictionary
            except json.JSONDecodeError:
                trip.itinerary = None  # Handle invalid JSON gracefully

    # Fetch images from the static/background/ folder
    background_folder = os.path.join(settings.STATICFILES_DIRS[0], 'background')
    images = [
        f"background/{file}" for file in os.listdir(background_folder)
        if file.endswith(('.jpg', '.jpeg'))
    ]

    return render(request, 'accounts/past_trips.html', {
        'trips': trips,
        'images_json': mark_safe(json.dumps(images)),
        'images': images # Although images_json is used by script, keep images for potential direct use
    })

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

def complete_trip(request, trip_id):
    if request.method == 'POST':
        # Retrieve the trip using the primary key (id) and ensure it belongs to the logged-in user
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        
        # Mark the trip as completed
        trip.completed = True
        trip.save()

        # Display a success message
        messages.success(request, f"The trip '{trip.trip_name or trip.location}' has been marked as completed.")

        # Redirect to the "Past Trips" page
        return redirect('past_trips')

@login_required
def trip_suggestions(request):
    # Fetch the most recent incomplete trip for the logged-in user
    current_trip = Trip.objects.filter(user=request.user, completed=False).order_by('-id').first()

    if not current_trip:
        # If no current trip exists, display a message and redirect to the trip planning page
        messages.info(request, "You have no current itinerary. Start planning your next adventure today!")
        return redirect('trip_preferences')  # Redirect to the trip planning page

    # Parse the itinerary JSON if it exists
    itinerary = None
    if current_trip.itinerary:
        try:
            itinerary = json.loads(current_trip.itinerary)
        except json.JSONDecodeError:
            itinerary = None  # Handle invalid JSON gracefully

    # Pass the current trip and itinerary to the template
    return render(request, 'accounts/trip_suggestions.html', {
        'trip': current_trip,
        'itinerary': itinerary
    })

@login_required
@require_POST # Ensure only POST requests are allowed
# @csrf_exempt # Temporarily disable CSRF for easier AJAX testing, add proper handling later
def remove_activity(request, trip_id, day_number, activity_index):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    try:
        itinerary_data = json.loads(trip.itinerary)
        day_str = str(day_number) # JSON keys are strings
        
        if day_str in itinerary_data['days'] and 0 <= activity_index < len(itinerary_data['days'][day_str]['activities']):
            removed_activity = itinerary_data['days'][day_str]['activities'].pop(activity_index)
            trip.itinerary = json.dumps(itinerary_data)
            trip.save()
            return JsonResponse({'status': 'success', 'message': f'Removed: {removed_activity.get("name", "Activity")}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid day or activity index.'}, status=400)
            
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return JsonResponse({'status': 'error', 'message': f'Failed to process request: {str(e)}'}, status=500)

@login_required
@require_POST
# @csrf_exempt # Temporarily disable CSRF
def add_activity(request, trip_id, day_number, suggestion_index):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    try:
        itinerary_data = json.loads(trip.itinerary)
        day_str = str(day_number) # JSON keys are strings

        if day_str in itinerary_data['days'] and 'suggestions' in itinerary_data['days'][day_str] and 0 <= suggestion_index < len(itinerary_data['days'][day_str]['suggestions']):
            
            # Get the suggestion AND remove it from the suggestions list in one step
            suggestion_to_add = itinerary_data['days'][day_str]['suggestions'].pop(suggestion_index)
            
            # Ensure the suggestion hasn't already been added (optional check)
            # if suggestion_to_add not in itinerary_data['days'][day_str]['activities']:
            
            # Add the suggestion to the main activities list
            itinerary_data['days'][day_str]['activities'].append(suggestion_to_add)
            
            # Save the modified itinerary (with suggestion removed and activity added)
            trip.itinerary = json.dumps(itinerary_data)
            trip.save()
            
            # Return the added activity data so the UI can update
            return JsonResponse({'status': 'success', 'added_activity': suggestion_to_add, 'new_index': len(itinerary_data['days'][day_str]['activities']) - 1})
            # else:
            #     return JsonResponse({'status': 'info', 'message': 'Activity already exists.'})
        else:
             return JsonResponse({'status': 'error', 'message': 'Invalid day or suggestion index.'}, status=400)

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return JsonResponse({'status': 'error', 'message': f'Failed to process request: {str(e)}'}, status=500)
