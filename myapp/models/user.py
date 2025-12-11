from django.db import models
from .employee import Employee
from django.contrib.auth.hashers import make_password, check_password

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=255)  # lưu hash
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=10)
    eid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    def set_password(self, raw_pass):
        self.password = make_password(raw_pass)

    def check_password(self, raw_pass):
        return check_password(raw_pass, self.password)
