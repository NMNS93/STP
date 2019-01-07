from django.db import models

# Create your models here.


class Patient(models.Model):
    pid = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    dob = models.DateField()
    notes = models.TextField()

    def __str__(self):
        return self.name

class Array(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.patient, self.date)
