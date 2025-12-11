from django.db import models

class TypeCustomer(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=20)
    minimumLevel = models.IntegerField()
    maximumLevel = models.IntegerField()
