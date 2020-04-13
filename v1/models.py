from django.db import models

# Create your models here.
# Create your models here.

class User(models.Model):
    """
    This class will store basic user information
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=1024, null=True)
    auth_token = models.CharField(max_length=1024, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True)
    username = models.CharField(max_length=1024, null=True)
    password = models.CharField(max_length=1024, null=True)


class TOY(models.Model):
    """
    TOY: Thinking Of You
    When a user sends a TOY request one of these objects are made
    """
    sender = models.ForeignKey('User', related_name='sender', on_delete=models.CASCADE)
    time_sent = models.DateTimeField(auto_now=False)
    receiver = models.ForeignKey('User', related_name='receiver', on_delete=models.CASCADE)