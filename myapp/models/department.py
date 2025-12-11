from django.db import models

class Department(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
