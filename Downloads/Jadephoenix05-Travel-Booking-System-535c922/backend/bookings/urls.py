from django.urls import path
from . import views

urlpatterns = [
    # This matches: http://localhost:8000/bookings/
    path('', views.get_user_bookings, name='get_user_bookings'),
]