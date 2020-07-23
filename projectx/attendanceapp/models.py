from django.db import models

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
    