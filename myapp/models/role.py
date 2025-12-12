from django.db import models

class Role(models.Model):
    role = models.CharField(max_length=20, primary_key=True)  # trùng với Users.role
    role_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20)

    def __str__(self):
        return self.role_name