from django.db import models


class Message(models.Model):
    content = models.TextField()
    created = models.DateTimeField(auto_now=True)
