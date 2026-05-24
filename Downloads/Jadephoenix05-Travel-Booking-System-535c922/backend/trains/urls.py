from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_trains, name='search_trains'), 
]