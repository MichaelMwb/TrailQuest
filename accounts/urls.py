from django.urls import path
from . import views
from .views import forgot_password, reset_password, trip_preferences_view


urlpatterns = [
    path('', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('signup/', views.signup, name='accounts.signup'),
    path('orders/', views.orders, name='accounts.orders'),
    path('forgot-password/', forgot_password, name='accounts.forgot_password'),
    path('reset-password/', reset_password, name='accounts.reset_password'),
    path('trip/', views.trip_preferences_view, name='trip_preferences'),
    path('trip/<int:trip_id>/complete/', views.complete_trip, name='complete_trip'),
    path('past-trips/', views.past_trips, name='past_trips'),
    path('trip-suggestions/', views.trip_suggestions, name='trip_suggestions'),
    path('saved-plans/', views.saved_plans, name='saved_plans'),
    path('saved-plans/<int:trip_id>/update/', views.update_trip, name='update_trip'),
    path('saved-plans/<int:trip_id>/delete/', views.delete_trip, name='delete_trip'),
    path('trip/<int:trip_id>/save/', views.save_trip_to_plans, name='save_trip_to_plans'),
]


