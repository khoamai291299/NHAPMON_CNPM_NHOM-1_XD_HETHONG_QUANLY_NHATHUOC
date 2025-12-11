from django.db import models
from .customer import Customer
from .employee import Employee

class Bill(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    dateOfcreate = models.DateField()
    cid = models.ForeignKey(Customer, on_delete=models.CASCADE)
    eid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    totalAmount = models.IntegerField(default=0)
