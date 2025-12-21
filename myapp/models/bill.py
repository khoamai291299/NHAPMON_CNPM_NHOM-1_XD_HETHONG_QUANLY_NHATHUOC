# myapp/models/bill.py
from django.db import models
from .customer import Customer
from .employee import Employee

class Bill(models.Model):
    id = models.CharField(primary_key=True, max_length=15)
    dateOfcreate = models.DateField(auto_now_add=True)

    cid = models.ForeignKey(Customer, on_delete=models.PROTECT)
    eid = models.ForeignKey(Employee, on_delete=models.PROTECT)

    PAYMENT_CHOICES = (
        ("cash", "Tiền mặt"),
        ("transfer", "Chuyển khoản"),
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="cash"
    )

    totalAmount = models.IntegerField(default=0)

    def __str__(self):
        return self.id
