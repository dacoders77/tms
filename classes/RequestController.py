# Receives requests from urls.py
# Adds a request to DB
# Runs a loop which waits for the response to be written to DB

from django.http import HttpResponse
from classes.Request import Request
import json

class PlaceOrder:
    @staticmethod
    def botstatus(request):
        requestPayload = json.dumps({
            "url": "botstatus"
        })
        Request.store(requestPayload)
        return HttpResponse(requestPayload)

    @staticmethod
    def placeorder(request, order_type, symbol, volume, direction):
        requestPayload = json.dumps({
            "url": "placeorder",
            "order_type": order_type,
            "symbol": symbol,
            "volume": volume,
            "direction": direction,
            "status": "new"
        })
        Request.store(requestPayload)
        return HttpResponse(requestPayload)

    @staticmethod
    def getquote(request, symbol):
        requestPayload = json.dumps({
            "url": "getquote"
        })
        Request.store(requestPayload)
        return HttpResponse(requestPayload)

    @staticmethod
    def cancelallorders(request):
        requestPayload = json.dumps({
            "url": "cancelallorders"
        })
        Request.store(requestPayload)
        return HttpResponse(requestPayload)

    def __delete__(self):
        return HttpResponse("")
