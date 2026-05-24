from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import Bus

def search_buses(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')

    buses = Bus.objects.filter(
        source = source,
        destination = destination
    ).values()

    return JsonResponse(list(buses),safe = False)
