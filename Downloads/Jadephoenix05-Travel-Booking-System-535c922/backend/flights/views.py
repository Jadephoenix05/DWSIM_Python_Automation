from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import Flight

def search_flights(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')

    flights = Flight.objects.filter(
        source = source,
        destination = destination
    ).values()

    return JsonResponse(list(flights),safe = False)