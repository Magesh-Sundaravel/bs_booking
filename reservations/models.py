from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.DateField()
    time = models.TimeField()
    service = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.service} on {self.day} at {self.time}"
