from django.db import models

# Create your models here.
class Train(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length = 100)
    destination = models.CharField(max_length = 100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.IntegerField()

    def __str__(self):
        return str.name