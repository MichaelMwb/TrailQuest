from django.urls import path
from . import views
from django.urls import path
from .views import forgot_password, reset_password

urlpatterns = [
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('signup/', views.signup, name='accounts.signup'),
    path('orders/', views.orders, name='accounts.orders'),
    path('forgot-password/', forgot_password, name='accounts.forgot_password'),
    path('reset-password/', reset_password, name='accounts.reset_password'),
]
