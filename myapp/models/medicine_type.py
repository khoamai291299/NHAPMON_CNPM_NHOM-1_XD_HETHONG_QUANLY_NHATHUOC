from django.db import models

class TypeMedicine(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=50, null=True, blank=True)
