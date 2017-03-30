
from django.contrib import admin

from .models import ItemList, QRcodeList ,BoughtItems, QRCodeRecord, QRcodeStatus, BoughtRecord, AdministratorControll



class UserPointsAdmin(admin.ModelAdmin):
    list_display = ["pk", "username", "real_name", "usable_points"]



class ItemAdmin(admin.ModelAdmin):
    list_display = ["pk","name","price", "remain","max_per_person",'image']

class QRCodeAdmin(admin.ModelAdmin):
    list_display = ["pk", "code_content","group","is_poster"]

class BoughtItemsAdmin(admin.ModelAdmin):
    list_display = ["pk", "user", "item_name", "item_quantity", "has_redeemed"]
    list_editable = ('has_redeemed',)

class BoughtRecordAdmin(admin.ModelAdmin):
    list_display = ["user", "item_name", "bought_time"]

class QRCodeRecordAdmin(admin.ModelAdmin):
    list_display = ["code_content", "time",  "points_got", "user"]

class CodeStatusAdmin(admin.ModelAdmin):
    list_display = ["code", "last_read", "user"]

class AdminControllAdmin(admin.ModelAdmin):
    list_display = ["name","group"]



admin.site.register(ItemList, ItemAdmin)
admin.site.register(QRcodeList, QRCodeAdmin)
admin.site.register(BoughtItems, BoughtItemsAdmin)
admin.site.register(BoughtRecord, BoughtRecordAdmin)
admin.site.register(QRCodeRecord, QRCodeRecordAdmin)
admin.site.register(QRcodeStatus, CodeStatusAdmin)
admin.site.register(AdministratorControll, AdminControllAdmin)