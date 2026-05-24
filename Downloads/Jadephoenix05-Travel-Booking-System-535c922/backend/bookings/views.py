from django.shortcuts import render

from django.http import JsonResponse
from .models import bookings 

def get_user_bookings(request):
    user_bookings = bookings.objects.all().values()
    
    return JsonResponse(list(user_bookings), safe=False)