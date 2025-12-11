from django.db import models
from .medicine_type import TypeMedicine
from .manufacturer import Manufacturer

class Medicine(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    content = models.IntegerField(null=True, blank=True)
    activeIngredient = models.CharField(max_length=30, null=True, blank=True)
    inputTime = models.DateField(null=True, blank=True)
    productionDate = models.DateField(null=True, blank=True)
    expirationDate = models.DateField(null=True, blank=True)
    unit = models.CharField(max_length=10, null=True, blank=True)

    tid = models.ForeignKey(TypeMedicine, on_delete=models.CASCADE)
    mid = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=0)
    importPrice = models.IntegerField(default=0)
    sellingPrice = models.IntegerField(default=0)
