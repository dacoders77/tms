from django.db import models

# Create your models here.

class Signal(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, null=True, blank=True)
    req_id = models.CharField(max_length=15, null=True, blank=True)
    request_payload = models.TextField(null=True, blank=True)
    response_payload = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=50, null=True, blank=True)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    direction = models.CharField(max_length=10, null=True, blank=True)
    order_place_date = models.DateTimeField(null=True, blank=True)
    order_status = models.CharField(max_length=20, null=True, blank=True)
    order_type = models.CharField(max_length=10, null=True, blank=True)
    order_id = models.CharField(max_length=40, null=True, blank=True)
    order_place_response = models.TextField(null=True, blank=True)
    order_execution_response = models.TextField(null=True, blank=True)
    order_execution_price = models.IntegerField(null=True, blank=True)

    # Pretty name output in console and in admin panel on the website
    def __str__(self):
        #return self.url + ' - ' + self.symbol
        #return(f"{self.id}  {self.created_at} {self.updated_at} {self.status}")
        return(str(self.id))



