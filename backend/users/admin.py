from django.contrib import admin
from users.models import Subscription


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user', 'author')
