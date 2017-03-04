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
            return Response('all ready autheticated')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')

        user = User.objects.create_user(username,email,password)

        EmailConfirmation.objects.verify_email_for_object(email, user)

        if user is not None and user.is_active:
            auth.login(request, user)
            return Response('Logged In')
        else:
            return Response('Not Logged In')


class LoginView(APIView):

    def get(self, request):
        return Response('Try Log In')

    def post(self,request):
        if request.user.is_authenticated():
            return Response('all ready autheticated')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request, user)
            return Response('Logged In')
        else:
            return Response('Not Logged In')

class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return HttpResponse("logged out", status=200)



def index(request):
    return render_to_response('index.html',locals())