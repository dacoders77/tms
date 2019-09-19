from django.contrib import admin
from .models import Signal, Log

# Register your models here.

@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
      list_display = ('id', 'req_id', 'status', 'url', 'request_payload', 'response_payload')
      ordering = ('id',)
      search_fields = ('id', 'url')


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
      list_display = ('id', 'message')



