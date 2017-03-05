from django.test import TransactionTestCase

from django.contrib.auth.models import User
from django.core import mail
from email_confirm_la.models import EmailConfirmation
from django.db import IntegrityError
from .models import UserProfile


class AccountTests(TransactionTestCase):


    def test_missing_signup_data(self):
        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456","department":"物理二" })
        self.assertEqual(response.status_code, 401)

        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456", "realname": "物理二"})
        self.assertEqual(response.status_code, 401)

        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456", "realname": "物理二","department":"物理二" })
        self.assertEqual(response.status_code, 200)

    def test_session_works(self):

        User.objects.create_user(username='hanson',password='hnhn123456',email='hnhn789@yahoo.com.tw')
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 406)

        response =  self.client.post("/accounts/login/",{"username":"hanson","password":"hnhn123456"})
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 406)

    def test_login_is_myself(self):
        User.objects.create_user(username='hanson', password='hnhn123456',email='hnhn789@yahoo.com.tw')
        response = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})
        self.assertContains(response,'hanson')


    def test_signup_same_account(self):
        User.objects.create_user(username='hanson', password='hnhn123456',email="hnhn789@yahoo.com.tw")
        response1 = self.client.post("/accounts/signup/", {"username": "hanson", "password": "hnhn123456",'realname':'郭郭','department':'物理二'})
        self.assertEqual(response1.status_code, 400)




    def test_reset_password(self):
        user = User.objects.create_user(username='hanson', password='hnhn123456', email="hnhn789@yahoo.com.tw")
        response1 = self.client.post("/accounts/changepassword/",
                                     {"oldpassword": "hnhn123456", "newpassword": "hnhn1234567"})
        self.assertEqual(response1.status_code, 400)


        response2 = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})
        response3 = self.client.post("/accounts/changepassword/",
                                     {"oldpassword": "hnhn123456", "newpassword": "hnhn1234567"})
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)

        response4 = self.client.post("/accounts/login/", {"username": "hanson", "password": "hnhn123456"})
        self.assertEqual(response4.status_code, 400)




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
        self.assertEqual(response2.status_code, 402)


        response3 = self.client.get("/email_confirmation/resend/b04202048/")
        self.assertEqual(response3.status_code, 200)


        self.assertIn('b04202048', mail.outbox[0].body)

    def test_wrong_resend_id(self):
        response = self.client.post("/accounts/signup/",
                                    {"username": "b04202048", "password": "hnhn123456", "realname": "郭郭",
                                     "department": "物理二"})
        self.assertEqual(response.status_code, 200)
        response3 = self.client.get("/email_confirmation/resend/b04202049/")
        self.assertEqual(response3.status_code, 407)


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
        self.assertEqual(response2.status_code, 402)

        response3 = self.client.get("/accounts/login/")
        self.assertEqual(response3.status_code, 402)

        SentEmail = EmailConfirmation.objects.get(email=user_email)
        key = SentEmail.confirmation_key
        response = self.client.get('/email_confirmation/key/'+key+'/')
        self.assertTemplateUsed(
            response,
            'email_confirm_la/email_confirmation_success.html'
        )

        response4 = self.client.get("/accounts/login/")
        self.assertEqual(response4.status_code, 200)

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
        self.assertRaises(IntegrityError)

