from django.db import models
from .employee import Employee
from .rollcall import RollCall

class DetailedAttendance(models.Model):
    eid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    days = models.DateField()
    checkin = models.TimeField(null=True, blank=True)
    checkout = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ('eid', 'days')


class SummaryAttendance(models.Model):
    rid = models.ForeignKey(RollCall, on_delete=models.CASCADE)
    eid = models.ForeignKey(Employee, on_delete=models.CASCADE)

    numOfworkDay = models.IntegerField(default=0)
    numOfdayOff = models.IntegerField(default=0)
    netSalary = models.IntegerField(default=0)

    class Meta:
        unique_together = ('rid', 'eid')
        db_table = "Summary_Attendance"

    def __str__(self):
        return f"{self.rid} - {self.eid}"