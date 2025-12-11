from django.db import models
from .bill import Bill
from .medicine import Medicine

class BillDetails(models.Model):
    bid = models.ForeignKey(Bill, on_delete=models.CASCADE)
    mid = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    unitPrice = models.IntegerField(default=0)
    totalAmount = models.IntegerField(default=0)

    class Meta:
        unique_together = ('bid', 'mid')
