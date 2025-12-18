from django.db import models
from .employee import Employee
from .role import Role
from django.contrib.auth.hashers import make_password, check_password

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, default="active")

    eid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "myapp_users"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
