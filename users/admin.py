from django.contrib import admin
from .models import CustomUser, Settings, Theme


class AdminUser(admin.ModelAdmin):
    list_display = ('id','email', 'last_name', 'first_name', 'is_staff', 'is_active', 'is_block')
# Register your models here.
admin.site.register(CustomUser, AdminUser)
admin.site.register(Settings)
admin.site.register(Theme)

