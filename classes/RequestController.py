# Receives requests from urls.py
# Adds a request to DB
# Runs a loop which waits for the response to be written to DB

from django.http import HttpResponse
from classes.Request import Request
import json
import time
import datetime
from ib.models import Signal

class PlaceOrder:

    @staticmethod
    def botstatus(request):
        requestPayload = json.dumps({
            "url": "botstatus"
        })
        # Add a record to rd
        res = Request.store(requestPayload)

        # loop here. Wait 20 sec
        for i in range(20):
            record = Signal.objects.get(id=res.id)
            print(record)
            if record.response_payload != None:
                return HttpResponse('Bot time: ' + str(datetime.datetime.now()) + '<br> Status: ' + record.response_payload)
            time.sleep(1)

        return HttpResponse('Bot status timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))


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
        res = Request.store(requestPayload)

        # loop here. Wait 20 sec
        for i in range(20):
            record = Signal.objects.get(id=res.id)
            print(record)
            if record.response_payload != None:
                return HttpResponse(
                    'Bot time: ' + str(datetime.datetime.now()) + '<br> Status: ' + record.response_payload)
            time.sleep(1)

        return HttpResponse(
            'Bot status timeout error. Response from the exchange has not been received within 10 seconds. ' + str(
                datetime.datetime.now()))

    @staticmethod
    def getquote(request, symbol):
        requestPayload = json.dumps({
            "url": "getquote",
            "symbol": symbol,
            "status": "new"
        })
        # Add a record to bd
        res = Request.store(requestPayload)

        # loop here. Wait 20 sec
        for i in range(20):
            record = Signal.objects.get(id=res.id)
            print(record)
            if record.response_payload != None:
                # Return only price
                return HttpResponse('Bot time: ' + str(datetime.datetime.now()) + '<br> Quote: ' + record.response_payload)
            time.sleep(1)

        return HttpResponse(
            'Getquote status timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))

    @staticmethod
    def cancelallorders(request):
        requestPayload = json.dumps({
            "url": "cancelall"
        })
        # Add a record to db
        res = Request.store(requestPayload)

        # loop here. Wait 20 sec
        for i in range(20):
            record = Signal.objects.get(id=res.id)
            print(record)
            if record.response_payload != None:
                # Return only price
                return HttpResponse(
                    'Bot time: ' + str(datetime.datetime.now()) + '<br> Cancel all: ' + record.response_payload)
            time.sleep(1)

        return HttpResponse(
            'Cancel all timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))



    def __delete__(self):
        return HttpResponse("")
