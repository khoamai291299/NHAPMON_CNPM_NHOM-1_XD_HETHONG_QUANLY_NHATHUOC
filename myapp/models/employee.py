from django.db import models
from .department import Department
from .position import Position

class Employee(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    startday = models.DateField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    sex = models.BooleanField(null=True)
    salary = models.IntegerField(null=True)

    did = models.ForeignKey(Department, on_delete=models.CASCADE)
    pid = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return self.name