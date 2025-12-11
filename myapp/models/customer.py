from django.db import models
from .customer_type import TypeCustomer

class Customer(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    tid = models.ForeignKey(TypeCustomer, on_delete=models.CASCADE)

    totalExpenditure = models.IntegerField(default=0)
    cumulativePoints = models.IntegerField(default=0)
