from django.db import models

class RollCall(models.Model):
    months = models.IntegerField()
    years = models.IntegerField()

    class Meta:
        unique_together = ('months', 'years')

    def __str__(self):
        return f"{self.months}/{self.years}"
