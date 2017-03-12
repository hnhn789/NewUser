from django.contrib.auth.models import User
from django.core import mail
from django.db import IntegrityError
from django.test import TransactionTestCase
from email_confirm_la.models import EmailConfirmation

from NewUser.models import ItemList, BoughtItems
from accounts.models import UserProfile


class AccountTests(TransactionTestCase):

    def test_missing_signup_data(self):
        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456","department":"物理二" })
        self.assertIn(str('註冊資料不完全').encode(), response.content)

        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456", "realname": "物理二"})
        self.assertIn(str('註冊資料不完全').encode(), response.content)

        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456", "realname": "物理二","department":"物理二" })
        self.assertIn(str('認證信已寄出').encode(), response.content)
    #
    # def test_session_works(self):
    #
    #     User.objects.create_user(username='hanson2',password='hnhn123456',email='hnhn789@yahoo.com.tw')
    #     response = self.client.get('/accounts/login/')
    #     self.assertIn(str('未登入').encode(), response.content)
    #
    #     response =  self.client.post("/accounts/login/",{"username":"hanson2","password":"hnhn123456"})
    #     self.assertIn(str('登入成功').encode(), response.content)
    #
    #     response = self.client.get('/accounts/login/')
    #     self.assertIn(str('已登入').encode(), response.content)
    #
    #     response = self.client.get('/accounts/logout/')
    #     self.assertIn(str('登出成功').encode(), response.content)
    #
    #     response = self.client.get('/accounts/login/')
    #     self.assertIn(str('未登入').encode(),response.content)

    def test_login_is_myself(self):
        User.objects.create_user(username='hanson', password='hnhn123456',email='hnhn789@yahoo.com.tw')
        response = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})
        self.assertIn(str('').encode(), response.content)

    def test_return_current_points(self):
        user= User.objects.create_user(username='hanson', password='hnhn123456', email='hnhn789@yahoo.com.tw')
        response = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})
        userprofile = UserProfile.objects.get(user=user)
        self.assertIsNotNone(userprofile)
        userprofile.usable_points = 10
        userprofile.save()
        response = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})

        profile2 = UserProfile.objects.get(user = user)
        self.assertEqual(profile2.usable_points,10)

    def test_signup_same_account(self):
        User.objects.create_user(username='hanson', password='hnhn123456',email="hnhn789@yahoo.com.tw")
        response1 = self.client.post("/accounts/signup/", {"username": "hanson", "password": "hnhn123456",'realname':'郭郭','department':'物理二'})
        self.assertIn(str('已被註冊').encode(), response1.content)




    def test_reset_password(self):
        user = User.objects.create_user(username='hanson', password='hnhn123456', email="hnhn789@yahoo.com.tw")
        response1 = self.client.post("/accounts/changepassword/",
                                     {"oldpassword": "hnhn123456", "newpassword": "hnhn1234567"})
        self.assertIn(str('請先重新登入').encode(), response1.content)


        response2 = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})
        response3 = self.client.post("/accounts/changepassword/",
                                     {"oldpassword": "hnhn123456", "newpassword": "hnhn1234567"})
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)

        response4 = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})
        self.assertIn(str('名稱或密碼有誤').encode(), response4.content)

    # def test_data_got(self):
    #     item1 = ItemList.objects.create(name='apple', price=500000, remain=76)
    #     item2 = ItemList.objects.create(name='pen', price=7200, remain=20)
    #     user = User.objects.create_user(username='b04202048', password='hnhn123456', email="hnhn789@yahoo.com.tw")
    #     response = self.client.post("/accounts/login/",
    #                                 {"username": "b04202048", "password": "hnhn123456", })
    #     print(response.content)


class EmailConfirmationTest(TransactionTestCase):
    def setUp(self):
        self.user_obj = User.objects.create_user(username='kiko_mizuhara')
        self.user_obj_2 = User.objects.create_user(username='odyx')
        self.user_email = 'kiko.mizuhara@gmail.com'
        self.user_email_2 = 'kiko.mizuhara@yahoo.com'


    def test_resend_email(self):

        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456", "realname": "郭郭",
                                     "department": "物理二"})
        self.assertEqual(response.status_code, 200)

        self.assertIn('b04202048',mail.outbox[0].body)
        mail.outbox.clear()

        response2 = self.client.post("/accounts/login/",
                                     {"username": "b04202048", "password": "hnhn123456", })
        self.assertIn(str('信箱尚未認證').encode(), response2.content)


        response3 = self.client.get("/accounts/email_confirmation/resend/b04202048/")
        self.assertEqual(response3.status_code, 200)


        self.assertIn('b04202048', mail.outbox[0].body)

    def test_wrong_resend_id(self):
        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456", "realname": "郭郭",
                                     "department": "物理二"})
        self.assertEqual(response.status_code, 200)
        response3 = self.client.get("/accounts/email_confirmation/resend/b04202049/")
        self.assertIn(str('請先註冊此信箱').encode(), response3.content)


    def test_confirmed_email(self):
        confirmation = EmailConfirmation.objects.verify_email_for_object(
            email=self.user_email,
            content_object=self.user_obj,
        )

        self.assertEqual(confirmation.content_object, self.user_obj)
        self.assertEqual(confirmation.email, self.user_email)
        self.assertEqual(confirmation.email_field_name, 'email')

        mail_obj = mail.outbox[0]

        self.assertIn(confirmation.confirmation_key, mail_obj.body)
        self.assertIn(self.user_email, mail_obj.body)

        confirmation.confirm()

        self.assertEqual(self.user_obj.email, self.user_email)


    def test_need_confirmation_email(self):
        user_email = "b04202048@ntu.edu.tw"

        response = self.client.post("/accounts/signup/",
                                     {"username": "b04202048", "password": "hnhn123456","realname":"郭郭" ,"department":"物理二"})
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='b04202048')
        self.assertEqual(user.email, '')

        response2 = self.client.post("/accounts/login/",
                                   {"username": "b04202048", "password": "hnhn123456", })
        self.assertIn(str('信箱尚未認證').encode(), response2.content)

        # response3 = self.client.get("/accounts/login/")
        # self.assertIn(str('信箱尚未認證').encode(), response3.content)

        SentEmail = EmailConfirmation.objects.get(email=user_email)
        key = SentEmail.confirmation_key
        response = self.client.get('/accounts/email_confirmation/key/'+key+'/')
        self.assertTemplateUsed(
            response,
            'email_confirm_la/email_confirmation_success.html'
        )
        # response4 = self.client.get("/accounts/login/")
        # self.assertEqual(response4.status_code, 200)



    def test_userprofile_created(self):
        user = User.objects.create_user(username='b04202048', password='hnhn123456', email="hnhn789@yahoo.com.tw")
        response = self.client.post("/accounts/login/",
                                     {"username": "b04202048", "password": "hnhn123456", })
        self.assertEqual(response.status_code, 200)

        userprofile = UserProfile.objects.get(user=user)
        self.assertIsNotNone(userprofile)

        response2 = self.client.post("/accounts/login/",
                                    {"username": "b04202048", "password": "hnhn123456", })

        self.assertEqual(response2.status_code, 200)
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=user)


class ReturnDataTest(TransactionTestCase):
    def test_update_shop_list(self):
        item1 = ItemList.objects.create(name='apple', price=500000, remain=76)
        item2 = ItemList.objects.create(name='pen', price=7200, remain=20)
        response = self.client.get("/shop/update/")
        self.assertIn(str('pen').encode(), response.content)

    def test_login_return_right_data(self):
        user = User.objects.create_user(username='b04202048', password='hnhn123456', email="hnhn789@yahoo.com.tw")
        response = self.client.post("/accounts/login/",
                                    {"username": "b04202048", "password": "hnhn123456", })
        self.assertEqual(response.status_code, 200)
        self.assertIn(str('000000000000 000000000000 00000000000').encode(), response.content)

    def test_logout_save_data(self):
        user = User.objects.create_user(username='b04202048', password='hnhn123456', email="hnhn789@yahoo.com.tw")
        response = self.client.post("/accounts/login/",
                                    {"username": "b04202048", "password": "hnhn123456", })
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/accounts/logout/",
                                    {"username": "b04202048", "stories": "0101010", })

        userprofile = UserProfile.objects.get(user = user)
        self.assertEqual(userprofile.stories,'0101010')

    def test_not_return_redeemed_item(self):
        user = User.objects.create_user(username='b04202048', password='hnhn123456', email="hnhn789@yahoo.com.tw")
        boughtitem = BoughtItems.objects.create(user=user,item_name=1,item_quantity=23,has_redeemed = False)
        response = self.client.post("/accounts/login/",
                                    {"username": "b04202048", "password": "hnhn123456", })
        self.assertEqual(response.status_code, 200)

        self.assertIn(str('23').encode(), response.content)

        boughtitem.has_redeemed=True
        boughtitem.save()

        response2= self.client.post("/accounts/login/",
                                    {"username": "b04202048", "password": "hnhn123456", })
        self.assertEqual(response2.status_code, 200)
        with self.assertRaises(AssertionError):
            self.assertIn(str('23').encode(), response2.content)






