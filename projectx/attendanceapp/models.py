from django.db import models
from datetime import datetime

# Create your models here.

class Org(models.Model):
    orgname = models.CharField(max_length=200)

    def __str__(self):
        return self.orgname


class Indlist(models.Model):
    username = models.CharField(max_length=200)
    orgname = models.CharField(max_length=200)
    imagee = models.ImageField(blank=True) 
    encoded = models.TextField(default='')

    def __str__(self):
        return self.username
    
class Orgattendance(models.Model):
    orgname = models.CharField(max_length=200)
    date = models.DateTimeField(default = datetime.today)

    def __str__(self):
        return self.orgname

class Userattendance(models.Model):
    orgname = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    status =models.BooleanField(default=False)
    date = models.DateTimeField(default = datetime.today)
    encoded = models.TextField(default='')

    def __str__(self):
        return self.username