import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Message(models.Model):
    title = models.CharField(max_length = 50)
    content = models.CharField(max_length = 200)
    pub_date = models.DateTimeField('date published')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    private = models.BooleanField()
    def __str__(self):
        return self.content