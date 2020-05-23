# Receives requests from urls.py
# Adds a request to DB
# Runs a loop which waits for the response to be written to DB

from django.http import HttpResponse
from classes.Request import Request
import logging # Default logger
import json
import time
import datetime
from django.db.models import Q
from ib.models import Signal


class PlaceOrder:

    errorMessage = 'Error: Request in progress' + str(datetime.datetime.now())
    timeOutMessage = 'Bot status timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now())

    @staticmethod
    def botstatus(request):
        logging.debug("Entered bot status. Code: xx88zz.")

        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "botstatus"
        })

        # Add a record to bd. Keep the whole added record in res
        res = PlaceOrder.store(requestPayload)

        # Wait for response from IB
        return PlaceOrder.waitLoop(res)

    @staticmethod
    def placeorder(request, order_type, exchange, symbol, volume, direction, currency, price=""):

        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "placeorder",
            "order_type": order_type,
            "exchange": exchange,
            "symbol": symbol,
            "currency": currency,
            "volume": volume,
            "price": price,
            "direction": direction,
            "status": "new"
        })

        res = PlaceOrder.store(requestPayload)
        return PlaceOrder.waitLoop(res)

    @staticmethod
    def getquote(request, exchange, symbol, currency):

        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "getquote",
            "exchange": exchange,
            "symbol": symbol,
            "currency": currency,
            "status": "new"
        })

        res = PlaceOrder.store(requestPayload)
        return PlaceOrder.waitLoop(res)

    @staticmethod
    def cancelallorders(request):

        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "cancelall"
        })

        res = PlaceOrder.store(requestPayload)
        return PlaceOrder.waitLoop(res)

    @staticmethod
    def getpositions(request, symbol=""):
        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "getpositions",
            "symbol": symbol
        })

        res = PlaceOrder.store(requestPayload)
        return PlaceOrder.waitLoop(res)

    @staticmethod
    def isLock():
        if Signal.objects.filter(Q(status='pending') | Q(status='new')).count() != 0:
            return True
        else:
            return False

    @staticmethod
    def store(requestPayload):
        try:
            return Request.store(requestPayload)
        except:
            error = 'RequestController.py. Update Model query error. Code: 43ee'
            print(error)
            logging.debug(error)

    @staticmethod
    def update(id):
        logging.debug("Update status to expired")
        try:
            return Request.update(id)
        except:
            error = 'RequestController.py. Update Model query error. Code: 43dd'
            print(error)
            logging.debug(error)

    # Wait for 10 sec until the response for the trading script is written to DB
    @staticmethod
    def waitLoop(res):
        for i in range(10):
            record = Signal.objects.get(id=res.id)
            print(record)
            if record.response_payload != None:
                return HttpResponse('Bot time: ' + str(datetime.datetime.now()) + '<br> Payload: ' + record.response_payload)
            time.sleep(1)

        PlaceOrder.update(res.id)
        return HttpResponse(PlaceOrder.timeOutMessage)

    def __delete__(self):
        return HttpResponse("")
