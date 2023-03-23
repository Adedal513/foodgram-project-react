from django.contrib import admin
from users.models import Subscribe


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user', 'author')
