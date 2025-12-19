from django.db import models
from .employee import Employee
from .role import Role
from django.contrib.auth.hashers import make_password, check_password


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default="active")

    eid = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        db_column="eid_id",
        related_name="user"
    )

    role_id = models.CharField(max_length=20)   # admin / seller

    class Meta:
        db_table = "myapp_users"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def phone(self):
        return self.eid.phone

    @property
    def role(self):
        return Role.objects.filter(role=self.role_id).first()

    def __str__(self):
        return self.username
