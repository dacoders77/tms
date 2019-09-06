from django.contrib import admin
from .models import Signal

# Register your models here.

#admin.site.register(Signal)
@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
      list_display = ('id', 'req_id', 'status', 'url', 'request_payload', 'response_payload')
      ordering = ('id',)
      search_fields = ('id', 'url')




