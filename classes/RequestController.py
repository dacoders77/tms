# Receives requests from urls.py
# Adds a request to DB
# Runs a loop which waits for the response to be written to DB

from django.http import HttpResponse
from classes.Request import Request


class PlaceOrder:
    @staticmethod
    def botstatus(request):
        Request.store()
        return HttpResponse("RequestController.py bot status ")

    @staticmethod
    def placeorder(request, order_type, symbol, volume, direction):
        return HttpResponse("hello from RequestController.py place_order:<br>"
                            + order_type + "<br>"
                            + symbol + "<br>"
                            + volume + "<br>"
                            + direction
                            )

    @staticmethod
    def getquote(request, symbol):
        return HttpResponse("RequestController.py get quote: " + symbol)

    @staticmethod
    def cancelallorders(request):
        return HttpResponse("RequestController.py cancel all orders")

    def __delete__(self):
        return HttpResponse("")
