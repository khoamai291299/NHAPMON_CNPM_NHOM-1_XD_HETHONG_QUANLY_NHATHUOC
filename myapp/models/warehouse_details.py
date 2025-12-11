from django.db import models
from .warehouse import WarehouseReceipt
from .medicine import Medicine

class WarehouseDetails(models.Model):
    wid = models.ForeignKey(WarehouseReceipt, on_delete=models.CASCADE)
    mid = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unitPrice = models.IntegerField()
    totalAmount = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('wid', 'mid')
