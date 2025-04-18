from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label="Birthdate"
    )

    class Meta:
        model = User
        fields = ('username', 'birthdate', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            birthdate = self.cleaned_data.get("birthdate")
            UserProfile.objects.create(user=user, birthdate=birthdate)
        return user

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username"
    )
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Birthdate"
    )

class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm New Password"
    )

from .models import TripPreferences

class TripPreferencesForm(forms.Form):
    location = forms.CharField(max_length=100, label="Location", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a location'}))
    duration = forms.IntegerField(min_value=1, max_value=20, label="Trip Duration (days)", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of days'}))
    
    ACTIVITIES_CHOICES = [
        ('hiking', 'Hiking'),
        ('camping', 'Camping'),
        ('both', 'Both'),
    ]
    activities = forms.ChoiceField(choices=ACTIVITIES_CHOICES, label="Choose Activity", widget=forms.Select(attrs={'class': 'form-control'}))
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES, label="Trail Difficulty", widget=forms.Select(attrs={'class': 'form-control'}))
    
    group_size = forms.IntegerField(min_value=1, label="Group Size", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'How many people?'}))
    
    trip_name = forms.CharField(max_length=100, required=False, label="Trip Name (optional)", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name your trip'}))