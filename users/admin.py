from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'parent', 'account_type', 'channel', 'fcmb_token')

