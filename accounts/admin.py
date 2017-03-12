from django.contrib import admin

from accounts.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):

    list_display = ["user", "usable_points","stories"]


admin.site.register(UserProfile, UserProfileAdmin)
