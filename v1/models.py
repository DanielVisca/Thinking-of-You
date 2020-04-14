from django.db import models
from secrets import token_urlsafe

# Create your models here.
# Create your models here.

class User(models.Model):
    """
    This class will store basic user information
    """
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=1024, null=True)
    auth_token = models.CharField(max_length=1024, default=None, null=True)
    phone_number = models.CharField(max_length=30, default='0000000000', null=True)
    password = models.CharField(max_length=1024, default='testpwd1', null=True)
    active = models.BooleanField(default=False, null=True)
 

class TOY(models.Model):
    """
    TOY: Thinking Of You
    When a user sends a TOY request one of these objects are made
    """
    sender = models.ForeignKey('User', related_name='sender', on_delete=models.CASCADE)
    time_sent = models.DateTimeField(auto_now=False)
    receiver = models.ForeignKey('User', related_name='receiver', on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)