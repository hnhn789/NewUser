from django.contrib import auth  # 別忘了import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response
from  django.views.generic.base import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import UserProfile
from django.db import IntegrityError

from email_confirm_la.models import EmailConfirmation

class ChangePasseordView(APIView):
    def post(self, request):

        oldpassword = request.POST.get('oldpassword', '')
        newpassword = request.POST.get('newpassword', '')

        if request.session.has_key('username'):
            user = User.objects.get(username=request.session['username'])
        else:
            return Response({"message": '請先重新登入', 'success': False}, status=400)

        if user is not None:

            if not user.check_password(oldpassword):
                return Response({"message": '原本密碼錯誤', 'success': False}, status=401)
            user.set_password(newpassword)
            user.save()

            return Response({"message": '重設成功', 'success': True}, status=200)


class ResendView(APIView):
    def get(self, request, username):
        email = username + '@ntu.edu.tw'
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({"message": '請先註冊此信箱', 'success': False}, status=407)

        EmailConfirmation.objects.verify_email_for_object(email, user)
        return Response({"message": '認證信已寄出！請確認！', 'success': True}, status=200)


class SignUpView(APIView):
    def post(self,request):
        if request.user.is_authenticated():
            auth.logout(request)

        if request.session.has_key('username'):
            del request.session['username']

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        realname = request.POST.get('realname', '')
        department = request.POST.get('department', '')
        email = username +'@ntu.edu.tw'

        if username == '' or password == '' or realname == '' or department=='':
            return Response({"message": '註冊資料不完全', 'success': False}, status=401)

        if User.objects.filter(username=username).exists():
            return Response({"message": '此信箱已被註冊過', 'success': False}, status=400)

        user = User.objects.create_user(username=username,password=password, first_name = department,last_name = realname)

        EmailConfirmation.objects.verify_email_for_object(email, user)

        if user is not None and user.is_active:
            return Response({"message":'認證信已寄出！請確認！','success':True}, status=200)
        else:
            return Response({"message": '註冊失敗', 'success': False}, status=400)


class LoginView(APIView):

    def get(self, request):
        if request.session.has_key('username'):
            user = User.objects.get(username=request.session['username'])

            if user is not None:
                if user.email == '':
                    return Response({"message": '信箱尚未認證', 'success': False}, status=402)
                auth.login(request, user)
                try:
                    UserProfile.objects.create(user = user)
                except IntegrityError:
                    pass
                return Response({"message":'已登入','success':True}, status=200)
            else:
                return Response({"message": '請登入', 'success': False}, status=400)
        else:
            return Response({"message": '未登入', 'success': False}, status=406)

    def post(self,request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            request.session['username'] = username
            if user.email == '':
                return Response({"message": '信箱尚未認證', 'success': False}, status=402)

            auth.login(request, user)
            try:
                UserProfile.objects.create(user=user)
            except IntegrityError:
                pass
            return Response({"message":'登入成功','success':True,'user':user.username}, status=200)
        else:
            return Response({"message": '使用者名稱或密碼有誤', 'success': False}, status=400)

class LogoutView(View):
    def get(self, request):
        try:
            del request.session['username']
        except:
            pass
        auth.logout(request)
        return HttpResponse("登出成功！", status=200)



def index(request):
    return render_to_response('index.html',locals())