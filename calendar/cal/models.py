from django.db import models

class Event(models.Model):
    calendar_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    is_recurring = models.BooleanField()

    class Meta:
        db_table = 'event'

    def __str__(self):
        return f"Event({self.calendar_name}, {self.name}, {self.start_date.isoformat()})"
