from django.contrib import auth  # 別忘了import auth
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render_to_response
from  django.views.generic.base import View
from rest_framework.response import Response
from rest_framework.views import APIView

from email_confirm_la.models import EmailConfirmation


class SignUpView(APIView):
    def post(self,request):
        if request.user.is_authenticated():
            return Response('已登入')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')

        if User.objects.filter(username=username).exists():
            return Response('此使用者名稱已註冊過')

        if User.objects.filter(email=email).exists():
            return Response('此信箱已被註冊過')

        user = User.objects.create_user(username,email,password)

        # EmailConfirmation.objects.verify_email_for_object(email, user)

        if user is not None and user.is_active:
            auth.login(request, user)
            return Response('認證信已寄出！')
        else:
            return Response('未登入')


class LoginView(APIView):

    def get(self, request):
        return Response('嘗試登入中')

    def post(self,request):
        if request.user.is_authenticated():
            return Response('已經登入')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request, user)
            return Response('登入成功！')
        else:
            return Response('使用者名稱或密碼有誤')

class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return HttpResponse("登出成功！", status=200)



def index(request):
    return render_to_response('index.html',locals())