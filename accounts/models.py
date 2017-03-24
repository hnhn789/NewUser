from django.contrib.auth.models import User
from django.db import models
from django.conf import settings



class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True,related_name='user_profile')
    usable_points = models.IntegerField(default=100)
    history_points = models.IntegerField(default=100)
    stories = models.CharField(default='00000000000000000000000000000000000',max_length=120)


