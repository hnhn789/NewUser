
from random import randint
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import pytz
import datetime
from NewUser.models import ItemList, BoughtItems, QRCodeRecord, QRcodeStatus, QRcodeList, BoughtRecord
from accounts.models import UserProfile


class BuyItem(APIView):
    def get(self, request, username, item_id):
        if (ItemList.objects.filter(pk=item_id).exists()):
            if (User.objects.filter(username=username).exists()):
                item = ItemList.objects.get(pk=item_id)
                if item.remain >= 1:
                    self.update_item(item_id)
                    time = self.save_to_user(username, item_id)
                    return Response({'messages':'購買成功','success':True, 'time': time},status=status.HTTP_200_OK)  ##TODO proper response
                else:
                    return Response({'messages':'此項目已售完','success':False})  # return Response(status=status.HTTP_409_CONFLICT) #TODO proper response
            else:
                return Response({'messages':'使用者不存在','success':False})
        else:
            return Response({'messages':'購買物品不存在','success':False},status=200)


    def update_item(self, item_id):
        item = ItemList.objects.get(pk=item_id)
        item.remain -= 1
        item.save()


    def save_to_user(self, username, item_id):
        user = User.objects.get(username=username)
        buyer = UserProfile.objects.get(user=user)

        boughtitem = BoughtItems.objects.filter(item_name=item_id)

        if boughtitem.filter(user=user).exists():
            bought_item_record = boughtitem.get(user=user)
        else:
            bought_item_record = BoughtItems(item_name=item_id, user=user)

        bought_item_record.item_quantity += 1
        bought_item_record.save()
        a = BoughtRecord(user=user, item_name=item_id)
        a.save()
        item = ItemList.objects.get(pk=item_id)
        buyer.usable_points -= item.price
        buyer.save()
        return a.bought_time


class QRCode(APIView):

    def get(self, request, username, qrcode):
        if (QRcodeList.objects.filter(code_content=qrcode).exists()):
            QRcode_status_data_list = self.got_correct_code(username, qrcode)

            if QRcode_status_data_list.filter(code=qrcode).exists():
                QRcode_status_data = QRcode_status_data_list.get(code=qrcode)
                logic = 0
            else:
                user = User.objects.get(username=username)
                QRcode_status_data = QRcodeStatus(code=qrcode, user=user)
                logic = 1

            old_time = QRcode_status_data.last_read
            now = datetime.datetime.now(pytz.utc)
            time_delta = now - old_time
            if ((time_delta.seconds >= 5) or logic):  # TODO QRcode cold down set here
                QRcode_status_data.last_read = now
                QRcode_status_data.save()
                point_recieved = randint(10, 50)  # point range set here
                user = User.objects.get(username=username)
                userprofile = UserProfile.objects.get(user=user)
                userprofile.usable_points += point_recieved
                userprofile.save()
                a = QRCodeRecord(code_content=qrcode, points_got=point_recieved, user=user)
                a.save()
                return Response({'messages':'成功得到點數！','success':True,'point_received':str(point_recieved),'time':now}, status=200)  # TODO proper response
            else:
                return Response({'messages':'此QRcode還不能使用','time':time_delta,'success':False},status=200)
        else:
            return Response({'messages':'QRcode不存在','success':False},status=200)  #TODO proper response

    def got_correct_code(self, username, qrcode):
        user = User.objects.get(username=username)
        QRcode_check_slug_list = QRcodeStatus.objects.filter(user=user)
        return QRcode_check_slug_list