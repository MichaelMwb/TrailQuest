from django.shortcuts import render, redirect
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

@login_required
@login_required
def logout(request):
    auth_logout(request)
    return redirect('movies.index')

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
            return redirect('movies.index')

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
