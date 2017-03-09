from django.contrib.auth.models import User
from django.core import mail
from django.db import IntegrityError
from django.test import TransactionTestCase
from email_confirm_la.models import EmailConfirmation
from accounts.models import UserProfile
from .models import ItemList, QRcodeList, BoughtItems, BoughtRecord
from time import sleep


class ShopTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='b04202048', password='hnhn123456', email='hnhn789@yahoo.com.tw')

    def test_buy(self):

        item_no = ItemList.objects.create(name="蛋糕",price=10,remain=0)
        item_yes = ItemList.objects.create(name="餅乾",price=10,remain=10)

        a = UserProfile(user=self.user,usable_points = 100)
        a.save()

        self.assertEqual(a.user, self.user)
        self.assertEqual(a.usable_points,100)

        response = self.client.get('/shop/b04202048/'+str(item_yes.pk)+'/')

        b = UserProfile.objects.get(user=self.user)
        self.assertEqual(b.usable_points, 90)

        item_yes_final = ItemList.objects.get(name=item_yes.name)

        c = BoughtItems.objects.count()
        d = BoughtRecord.objects.count()

        self.assertNotEqual(c, 0)
        self.assertNotEqual(d, 0)

        response2 = self.client.get('/shop/b04202048/' + str(item_yes.pk) + '/')
        e = BoughtItems.objects.get(user=self.user)
        self.assertEqual(e.item_quantity, 2)

        response3 = self.client.get('/shop/b04202048/4/')
        self.assertEqual(response3.status_code, 401)
        self.assertEqual(item_yes_final.remain, 9)
        self.assertEqual(response.status_code, 200)


    def test_qrcode_cd(self):
        a = QRcodeList.objects.create(code_content='Physics')
        b = UserProfile(user=self.user, usable_points=100)
        b.save()

        response = self.client.get('/QRcode/b04202048/Physicszzz/')
        self.assertEqual(response.status_code, 401)

        response = self.client.get('/QRcode/b04202048/Physics/')
        self.assertEqual(response.status_code, 200)

        sleep(3)

        response2 = self.client.get('/QRcode/b04202048/Physics/')
        self.assertEqual(response2.status_code, 400)

        sleep(6)

        response3 = self.client.get('/QRcode/b04202048/Physics/')
        self.assertEqual(response3.status_code, 200)




