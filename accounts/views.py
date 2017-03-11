from django.contrib import auth  # 別忘了import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render_to_response
from  django.views.generic.base import View
from email_confirm_la.models import EmailConfirmation
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile


class ChangePasseordView(APIView):
    def post(self, request):

        oldpassword = request.POST.get('oldpassword', '')
        newpassword = request.POST.get('newpassword', '')

        if request.session.has_key('username'):
            user = User.objects.get(username=request.session['username'])
        else:
            return Response({"messages": '請先重新登入','success': False}, status=200)

        if user is not None:

            if not user.check_password(oldpassword):
                return Response({"messages": '原本密碼錯誤', 'success': False}, status=200)
            user.set_password(newpassword)
            user.save()

            return Response({"messages": '重設成功', 'success': True}, status=200)


class ResendView(APIView):
    def get(self, request, username):
        email = username + '@ntu.edu.tw'
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({"messages": '請先註冊此信箱', 'success': False}, status=200)

        EmailConfirmation.objects.verify_email_for_object(email, user)
        return Response({"messages": '認證信已寄出！請確認！', 'success': True}, status=200)


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
            return Response({"messages": '註冊資料不完全', 'success': False}, status=200)

        if User.objects.filter(username=username).exists():
            return Response({"messages": '此信箱已被註冊過', 'success': False}, status=200)

        user = User.objects.create_user(username=username,password=password, first_name = department,last_name = realname)

        EmailConfirmation.objects.verify_email_for_object(email, user)

        if user is not None and user.is_active:
            return Response({"messages":'認證信已寄出！請確認！','success':True}, status=200)
        else:
            return Response({"messages": '註冊失敗，請重試', 'success': False}, status=200)


class LoginView(APIView):
    def dump_data(self):
        return

    def get(self, request):
        if request.session.has_key('username'):
            user = User.objects.get(username=request.session['username'])

            if user is not None:
                if user.email == '':
                    return Response({"messages": '信箱尚未認證', 'success': False}, status=200)
                auth.login(request, user)
                try:
                    ProfileUser = UserProfile.objects.get(user=user)
                except ObjectDoesNotExist:
                    ProfileUser = UserProfile.objects.create(user=user)
                points = ProfileUser.usable_points
                self.dump_data()
                return Response({"messages":'已登入','success':True, 'points':points}, status=200)
            else:
                return Response({"messages": '請登入', 'success': False}, status=200)
        else:
            return Response({"messages": '未登入', 'success': False}, status=200)

    def post(self,request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            request.session['username'] = username
            if user.email == '':
                return Response({"messages": '信箱尚未認證', 'success': False}, status=200)

            auth.login(request, user)
            try:
                ProfileUser = UserProfile.objects.get(user=user)
            except ObjectDoesNotExist:
                ProfileUser = UserProfile.objects.create(user=user)
            points = ProfileUser.usable_points
            self.dump_data()
            return Response({"messages":'登入成功','success':True,'user':user.username,'points':points}, status=200)
        else:
            return Response({"messages": '使用者名稱或密碼有誤', 'success': False}, status=200)

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