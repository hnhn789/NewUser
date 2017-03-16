from django.contrib.auth.models import User
from django.core import mail
from django.db import IntegrityError
from django.test import TransactionTestCase
from email_confirm_la.models import EmailConfirmation
from accounts.models import UserProfile
from .models import ItemList, QRcodeList, BoughtItems, BoughtRecord, AdministratorControll, QRCodeRecord
from time import sleep


class ShopTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='b04202048', password='hnhn123456', email='hnhn789@yahoo.com.tw')
        self.user2 = User.objects.create_user(username='b04202049', password='hnhn123456', email='hnh789@yahoo.com.tw')
        self.group_controll = AdministratorControll.objects.create(group=0)


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
        self.assertIn(str('物品不存在').encode(), response3.content)
        self.assertEqual(item_yes_final.remain, 9)
        self.assertEqual(response.status_code, 200)

    def test_two_user_using_same_qrcode(self):
        a = QRcodeList.objects.create(code_content='Physics',is_poster=True)
        b = QRcodeList.objects.create(code_content='Night', is_poster=False)
        c = UserProfile.objects.create(user = self.user)
        d = UserProfile.objects.create(user=self.user2)


        response = self.client.get('/QRcode/b04202048/Physics/')
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get('/QRcode/b04202049/Physics/')
        self.assertEqual(response2.status_code, 200)

    def test_qrcode_cd(self):
        a = QRcodeList.objects.create(code_content='Physics')
        b = UserProfile(user=self.user, usable_points=100)
        b.save()

        response = self.client.get('/QRcode/b04202048/Physicszzz/')
        self.assertIn(str('不存在').encode(), response.content)

        response = self.client.get('/QRcode/b04202048/Physics/')
        self.assertEqual(response.status_code, 200)

        print(response.content)
        # sleep(3)
        #
        # response2 = self.client.get('/QRcode/b04202048/Physics/')
        # self.assertIn(str('還不能使用').encode(), response2.content)
        #
        # sleep(6)
        #
        # response3 = self.client.get('/QRcode/b04202048/Physics/')
        # self.assertEqual(response3.status_code, 200)

    def test_is_poster_or_not(self):
        a = QRcodeList.objects.create(code_content='Physics',is_poster=True)
        d = QRcodeList.objects.create(code_content='Night', is_poster=False)
        b = UserProfile(user=self.user, usable_points=0)
        b.save()

        response = self.client.get('/QRcode/b04202048/Physics/')
        self.assertEqual(response.status_code, 200)
        c = UserProfile.objects.get(user = self.user)
        self.assertEqual(c.usable_points, 5)

        response = self.client.get('/QRcode/b04202048/Night/')
        self.assertEqual(response.status_code, 200)
        e = UserProfile.objects.get(user=self.user)
        self.assertNotEqual(e.usable_points, 5)


    def test_not_enough_money(self):
        item = ItemList.objects.create(name="蛋糕", price=10, remain=2)

        a = UserProfile(user=self.user, usable_points=5)
        a.save()

        response = self.client.get('/shop/b04202048/' + str(item.pk) + '/')
        self.assertIn(str('您的點數不足').encode(), response.content)


    def test_change_qrcode_admin_group(self):
        a = QRcodeList.objects.create(code_content='Physics', is_poster=True, group=0)
        d = QRcodeList.objects.create(code_content='Night', is_poster=False, group=1)
        b = UserProfile(user=self.user, usable_points=0)
        b.save()

        response = self.client.get('/QRcode/b04202048/Physics/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/QRcode/b04202048/Night/')
        self.assertIn(str('此QRcode已無法使用').encode(), response.content)

    # def test_point_gets_smaller(self):
    #     a = QRcodeList.objects.create(code_content='Physics', is_poster=True, group=0)
    #     d = QRcodeList.objects.create(code_content='Night', is_poster=False, group=1)
    #     b = UserProfile(user=self.user, usable_points=0)
    #     b.save()
    #
    #     response = self.client.get('/QRcode/b04202048/Physics/')
    #     self.assertIn(str('成功').encode(), response.content)
    #
    #     count = QRCodeRecord.objects.filter(user=self.user).count()
    #
    #     self.assertEqual(count,1)
    #
    #     sleep(6)
    #
    #     response2 = self.client.get('/QRcode/b04202048/Physics/')
    #     self.assertIn(str('成功').encode(), response2.content)
    #
    #     count2 = QRCodeRecord.objects.filter(user=self.user).filter(code_content="Physics").count()
    #
    #     self.assertEqual(count2, 2)



