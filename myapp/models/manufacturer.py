from django.db import models

class Manufacturer(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    country = models.CharField(max_length=20, null=True, blank=True)
