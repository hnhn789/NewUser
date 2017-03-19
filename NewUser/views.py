
from random import randint
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import pytz
import datetime
from NewUser.models import ItemList, BoughtItems, QRCodeRecord, QRcodeStatus, QRcodeList, BoughtRecord, AdministratorControll
from accounts.models import UserProfile
from NewUser.serializers import ItemListSerializer


class BuyUpdate(APIView):

    def get(self, request):
        itemlists = ItemList.objects.all()
        serializer = ItemListSerializer(itemlists, many=True)
        return Response(serializer.data)
        # return Response({'messages': '購買物品不存在', 'success': False}, status=200)



class BuyItem(APIView):
    def get(self, request, username, item_id):
        if (ItemList.objects.filter(pk=item_id).exists()):
            user = User.objects.get(username=username)
            if (user is not None):
                item = ItemList.objects.get(pk=item_id)
                if item.remain >= 1:
                    buyer = UserProfile.objects.get(user=user)
                    if (buyer.usable_points >= item.price):
                        boughtitems = BoughtItems.objects.filter(user=user).filter(item_name=item.id).filter(has_redeemed=False)
                        if(boughtitems.exists() and boughtitems[0].item_quantity > (item.max_per_person-1)):
                            return Response({'messages': '很抱歉！您已超過此項目購買上限！請選購其他商品。', 'success': False})
                        else:
                            self.update_item(item_id)
                            time = self.save_to_user(username, item_id)
                            return Response({'messages':'購買成功！','success':True, 'time': time},status=status.HTTP_200_OK)  ##TODO proper response
                    else:
                        return Response({'messages': '很抱歉！您的點數不足！', 'success': False})
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

        boughtitem = BoughtItems.objects.filter(item_name=item_id).filter(user=user).filter(has_redeemed=False)

        if boughtitem.exists():
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
        GroupObject = AdministratorControll.objects.get(name='open_group')
        current_group = GroupObject.group
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'messages': '網路問題，請重新登入', 'success': False}, status=200)
        time_filter = QRCodeRecord.objects.filter(user=user).filter(code_content=qrcode)
        if time_filter is not None:
            times = int(time_filter.count())
        else:
            times=0

        try:
            qrcodeModel = QRcodeList.objects.get(code_content=qrcode)
        except ObjectDoesNotExist:
            return Response({'messages': 'QRcode不存在', 'success': False}, status=200)
        if (qrcodeModel is not None and qrcodeModel.group == current_group):
            QRcode_status_data_list = self.got_correct_code(username, qrcode)

            if QRcode_status_data_list.filter(code=qrcode).exists():
                QRcode_status_data = QRcode_status_data_list.get(code=qrcode)
                logic = 0
            else:
                QRcode_status_data = QRcodeStatus(code=qrcode, user=user)
                logic = 1

            old_time = QRcode_status_data.last_read
            now = datetime.datetime.now(pytz.utc)
            time_delta = now - old_time
            remain_hour = int(time_delta.seconds/3600)
            remain_minutes = int((time_delta.seconds-remain_hour*3600)/60)
            remain_seconds = int((time_delta.seconds-remain_hour*3600-remain_minutes*60))
            time_message = str(3-remain_hour)+ '小時' + str(59-remain_minutes) + '分' + str(59-remain_seconds) + "秒"
            wait_message = '此QRcode冷卻中，還不能使用...剩餘時間：'+time_message
            if ((time_delta.seconds >= 4*60*60) or logic):  # TODO QRcode cold down set here
                QRcode_status_data.last_read = now
                QRcode_status_data.save()
                QR = QRcodeList.objects.get(code_content=qrcode)
                if (QR.is_poster):
                    point_recieved = 5
                else:
                    random = randint(20, 30)
                    power = 0.7**int(times)
                    point_recieved = int(random*power)

                user = User.objects.get(username=username)
                userprofile = UserProfile.objects.get(user=user)
                userprofile.usable_points += point_recieved
                userprofile.history_points += point_recieved
                userprofile.save()
                a = QRCodeRecord(code_content=qrcode, points_got=point_recieved, user=user)
                a.save()
                return Response({'messages':'成功得到點數！','success':True,'point_received':str(point_recieved),'time':now}, status=200)  # TODO proper response
            else:
                return Response({'messages':str(wait_message),'time':time_delta,'success':False},status=200)
        else:
            return Response({'messages':'此QRcode已無法使用','success':False},status=200)  #TODO proper response

    def got_correct_code(self, username, qrcode):
        user = User.objects.get(username=username)
        QRcode_check_slug_list = QRcodeStatus.objects.filter(user=user)
        return QRcode_check_slug_list