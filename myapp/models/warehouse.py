from django.db import models
from .employee import Employee

class WarehouseReceipt(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    inputDay = models.DateField(null=True, blank=True)
    eid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    totalImport = models.IntegerField(default=0)
    