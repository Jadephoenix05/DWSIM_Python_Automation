from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from .models import Train

def search_trains(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')

    trains = Train.objects.filter(
        source = source,
        destination = destination
    ).values()

    return JsonResponse(list(trains),safe = False)