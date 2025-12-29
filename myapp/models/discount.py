from django.db import models
from .customer_type import TypeCustomer


class Discount(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    startday= models.DateTimeField(null=True, blank=True)
    endday= models.DateTimeField(null=True, blank=True)
    value= models.IntegerField()
    tid = models.ForeignKey(TypeCustomer, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


