from django.contrib import admin
from .models import *

class ForwardInline(admin.TabularInline):
    model = Forward
    extra = 2 # how many rows to show
    fk_name = "this_message"

class DialogAdmin(admin.ModelAdmin):
    inlines = [ForwardInline]

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Dialog, DialogAdmin)
admin.site.register(Forward)
# Register your models here.
