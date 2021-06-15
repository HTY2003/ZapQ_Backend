from django.db import models


class Queue(models.Model):
    queue_name = models.CharField(max_length=200)
    queue_desc = models.CharField(max_length=200)
    queue_qty = models.PositiveIntegerField()
    queue_eta = models.PositiveIntegerField()  # in minutes
    queue_lat = models.PositiveIntegerField()
    queue_long = models.PositiveIntegerField()
