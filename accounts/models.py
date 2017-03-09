from django.contrib.auth.models import User
from django.db import models
from django.conf import settings



class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='user_profile')
    usable_points = models.IntegerField(default=0)



