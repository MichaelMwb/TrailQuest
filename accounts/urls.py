from django.urls import path
from . import views
from .views import (
    forgot_password, reset_password, trip_preferences_view,
    remove_activity, add_activity
)


urlpatterns = [
    path('', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('signup/', views.signup, name='accounts.signup'),
    path('orders/', views.orders, name='accounts.orders'),
    path('forgot-password/', forgot_password, name='accounts.forgot_password'),
    path('reset-password/', reset_password, name='accounts.reset_password'),
    path('trip/', views.trip_preferences_view, name='trip_preferences'),
    path('trip-suggestions/', views.trip_suggestions, name='trip_suggestions'),
    path('past-trips/', views.past_trips, name='past_trips'),
    path('complete_trip/<int:trip_id>/', views.complete_trip, name='complete_trip'),
    path('trip/<int:trip_id>/day/<int:day_number>/remove/<int:activity_index>/', 
         remove_activity, name='remove_activity'),
    path('trip/<int:trip_id>/day/<int:day_number>/add/<int:suggestion_index>/', 
         add_activity, name='add_activity'),
]


