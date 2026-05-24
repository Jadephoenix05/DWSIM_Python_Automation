from django.db import models

# Create your models here.
class Booking(models.Model):
    passenger_name = models.CharField(max_length = 100)
    bus = models.ForeignKey('buses.Bus', on_delete=models.CASCADE, null=True, blank=True)
    train = models.ForeignKey('trains.Train', on_delete=models.CASCADE, null=True, blank=True)
    flight = models.ForeignKey('flights.Flight', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return self.passenger_name 
    