from django.db import models
from .customer import Customer
from .employee import Employee

class Bill(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    dateOfcreate = models.DateField(auto_now_add=True)
    cid = models.ForeignKey(Customer, on_delete=models.PROTECT)
    eid = models.ForeignKey(Employee, on_delete=models.PROTECT)
    totalAmount = models.IntegerField(default=0)

    def __str__(self):
        return self.id

