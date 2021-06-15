from django.db import models
from django.contrib.auth import get_user_model
from .serializers import User


User = get_user_model()


class Queue(models.Model):
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=200)
    eta = models.PositiveIntegerField()  # in minutes
    lati = models.DecimalField(max_digits=9, decimal_places=6)
    longi = models.DecimalField(max_digits=9, decimal_places=6)
    creator = models.ForeignKey(User)
    paused = models.BooleanField()
    ended = models.BooleanField()
    users = models.ManyToManyField(User, related_name='queues')
    allusers = models.ManyToManyField(User, related_name='allqueues')
