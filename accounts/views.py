from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ForgotPasswordForm
from .models import UserProfile
from django.contrib.auth import update_session_auth_hash
from .forms import PasswordResetForm
from .forms import TripPreferencesForm
from openai import OpenAI
import json
from TRAILQUEST.settings import OPENAI_API_KEY
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def logout(request):
    auth_logout(request)
    return redirect('accounts.login')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
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

from django.shortcuts import render, redirect
from .forms import TripPreferencesForm
from .models import TripPreferences, Trip
from openai import OpenAI
import json

@login_required
def trip_preferences_view(request):
    client = OpenAI(
        api_key = OPENAI_API_KEY
    )

    if request.method == 'POST':
        form = TripPreferencesForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Construct the prompt
            prompt = f"""Create a detailed itinerary for a {cd['duration']}-day trip to {cd['location']}.
            Trip name: {cd['trip_name']}
            Activity type: {cd['activities']}
            Difficulty level: {cd['difficulty']}
            Group size: {cd['group_size']}
            
            Please provide a detailed day-by-day itinerary in the following JSON format:
            {{
                "name": "trip name",
                "location": "location name",
                "difficulty": "easy/medium/hard",
                "days": {{
                    "1": [
                        {{
                            "name": "activity name",
                            "location": "activity location",
                            "description": "activity description",
                            "duration": "duration in hours"
                        }}
                    ]
                }}
            }}"""

            # Call OpenAI API
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert trail and camping trip planner."},
                        {"role": "user", "content": prompt}
                    ]
                )

                # Debugging: Log the response
                print("OpenAI API Response:", response)

                # Extract and clean the response content
                raw_content = response.choices[0].message.content
                cleaned_content = raw_content.strip("```").strip("json").strip()  # Remove backticks and "json"

                # Parse the cleaned response
                itinerary_data = json.loads(cleaned_content)

                for day in itinerary_data['days']:
                    for i in range(len(itinerary_data['days'][day])):
                        # Add a Google Maps link to the location
                        itinerary_data['days'][day][i]['location'] = "https://www.google.com/maps/search/?api=1&query=" + itinerary_data['days'][day][i]['location'].lower().replace(" ", "+")

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

                # Redirect to the trip suggestions page
                return redirect('trip_suggestions')

            except json.JSONDecodeError as jde:
                print("JSONDecodeError:", jde)
                messages.error(request, "The itinerary format is invalid. Please try again.")
            except Exception as e:
                print("Error:", e)
                messages.error(request, "An error occurred while generating the itinerary. Please try again.")
    else:
        form = TripPreferencesForm()

    return render(request, 'accounts/trip_preferences.html', {'form': form})

from django.shortcuts import render
from .models import Trip  # Assuming you have a Trip model

@login_required
def past_trips(request):
    # Retrieve completed trips for the logged-in user, ordered by most recent first
    trips = Trip.objects.filter(user=request.user, completed=True).order_by('-id')
    return render(request, 'accounts/past_trips.html', {'trips': trips})

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

def complete_trip(request, trip_id):
    if request.method == 'POST':
        # Retrieve the trip using the primary key (id) and ensure it belongs to the logged-in user
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        
        # Mark the trip as completed
        trip.completed = True
        trip.save()

        # Redirect to the "Past Trips" page
        return redirect('past_trips')

@login_required
def trip_suggestions(request):
    # Fetch the most recent incomplete trip for the logged-in user
    current_trip = Trip.objects.filter(user=request.user, completed=False).order_by('-id').first()

    if not current_trip:
        # If no current trip exists, redirect to the "Plan a Trip" page
        return redirect('trip_preferences')

    # Parse the itinerary JSON if it exists
    itinerary = None
    if current_trip.itinerary:
        itinerary = json.loads(current_trip.itinerary)

    # Pass the current trip and itinerary to the template
    return render(request, 'accounts/trip_suggestions.html', {
        'trip': current_trip,
        'itinerary': itinerary
    })
