
from django.conf import settings
from django.db import models
import datetime
import pytz

class ItemList(models.Model):
    name = models.CharField(max_length=100,blank=True)
    price = models.IntegerField(default=0)
    remain = models.IntegerField(default=0)
    image = models.CharField(max_length=200,default='https://firebasestorage.googleapis.com/v0/b/sibo-5e145.appspot.com/o/p_coin.png?alt=media&token=682579a3-23fa-4a96-a758-5bc07610a556')

    def __str__(self):
        return self.name

class BoughtItems(models.Model):
    item_name = models.IntegerField(default=0)
    item_quantity = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bought_items')
    has_redeemed = models.BooleanField(default=False)


class QRCodeRecord(models.Model):
    code_content = models.CharField(max_length=40, unique=False)
    time = models.DateTimeField(auto_now_add=True, editable=False)
    points_got = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='qrcode_record')

class QRcodeStatus(models.Model):
    code = models.SlugField(max_length=40)
    last_read = models.DateTimeField(default=datetime.datetime.now(pytz.utc), editable=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='qrcode_status')

class QRcodeList(models.Model):
    code_content = models.SlugField(max_length=40, unique=True)
    is_poster = models.BooleanField(default=False)

    def __str__(self):
        return self.code_content

class BoughtRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bought_record')
    item_name = models.IntegerField(default=0)
    bought_time = models.DateTimeField(auto_now_add=True, editable=False)