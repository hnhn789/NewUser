from django.contrib import auth  # 別忘了import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render_to_response
from email_confirm_la.models import EmailConfirmation
from rest_framework.response import Response
from rest_framework.views import APIView
from NewUser.models import BoughtItems
from NewUser.serializers import BoughtItemsSerializer

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
            return Response({'success': False", messages": '註冊資料不完全'}, status=200)

        if User.objects.filter(username=username).exists():
            return Response({'success': False, "messages": '此信箱已被註冊過'}, status=200)

        user = User.objects.create_user(username=username,password=password, first_name = department,last_name = realname)

        if user is not None and user.is_active:

            EmailConfirmation.objects.verify_email_for_object(email, user)
            return Response({'success':True,"messages":'認證信已寄出！請至學校信箱確認！'}, status=200)
        else:
            return Response({'success': False,"messages": '註冊失敗，請重試'}, status=200)


class LoginView(APIView):
    # def dump_data(self):
    #     name_list = {}
    #     price_list = {}
    #     remain_list = {}
    #
    #     for i in range(1, ItemList.objects.count()+1):
    #         name_list[i] = ItemList.objects.get(pk=i).name
    #         price_list[i] = ItemList.objects.get(pk=i).price
    #         remain_list[i] = ItemList.objects.get(pk=i).remain
    #
    #     data = {"name": name_list, "price": price_list, "remain": remain_list}
    #     return data

    def data_points_story_shop(self, user):
        try:
            ProfileUser = UserProfile.objects.get(user=user)
        except ObjectDoesNotExist:
            ProfileUser = UserProfile.objects.create(user=user)
        points = ProfileUser.usable_points
        stories = ProfileUser.stories

        boughtitems = BoughtItems.objects.filter(user = user).filter(has_redeemed=False)
        serializer = BoughtItemsSerializer(boughtitems, many=True)
        return points, stories, serializer.data

    def post(self,request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            request.session['username'] = username
            if user.email == '':
                return Response({'success': False,"messages": '信箱尚未認證'}, status=200)
            auth.login(request, user)

            points, stories, boughtitems = self.data_points_story_shop(user)

            return Response({'success': True,'stories':stories,'points':points,"messages": '登入成功','boughtitems': boughtitems, 'username':username})
        else:
            return Response({'success': False,"messages": '使用者名稱或密碼有誤'}, status=200)

class LogoutView(APIView):
    def post(self, request):
        username = request.POST.get('username', '')
        stories = request.POST.get('stories', '')
        # points = request.POST.get('points', '')
        try:
            user = User.objects.get(username = username)
            userprofile = UserProfile.objects.get(user = user)
            userprofile.stories = stories
            # userprofile.usable_points = points
            userprofile.save()
        except:
            return Response({"messages": "登出失敗，請重試！", 'success': False}, status=200)
        try:
            del request.session['username']
        except:
            pass
        auth.logout(request)
        return Response({'success': True,"messages": "登出成功！"}, status=200)



def index(request):
    return render_to_response('index.html',locals())
