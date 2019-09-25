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

    errorMessage = 'Error: Request is in progress. You can not send more than one request at a time.<br>' \
                   'Possible problem 1: requests are not handled with IB and no response is received form IB Gateway.<br>'\
                   'Possible problem 2: IB Gateway is not connected. Check the status in VNC.<br>' \
                   'Please delete all pending tasks manually in order to continue.<br>'\
                   + str(datetime.datetime.now())

    @staticmethod
    def botstatus(request):

        # If there are pending tasks active
        if PlaceOrder.isLock(request): return HttpResponse(PlaceOrder.errorMessage)

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

        # If there are pending tasks active
        if PlaceOrder.isLock(request): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "placeorder",
            "order_type": order_type,
            "symbol": symbol,
            "volume": volume,
            "direction": direction,
            "status": "new"
        })

        res = Request.store(requestPayload)  # Add the record to db

        # loop here. Wait 20 sec
        for i in range(20):
            record = Signal.objects.get(id=res.id) # Check the created record
            print(record)
            if record.response_payload != None:
                return HttpResponse(
                    'Bot time: ' + str(datetime.datetime.now()) + '<br> Status: ' + record.response_payload)
            time.sleep(1)

        # Release the lock
        return HttpResponse(
            'Place timeout error. Response from the exchange has not been received within 10 seconds. ' + str(
                datetime.datetime.now()))

    @staticmethod
    def getquote(request, symbol):

        # If there are pending tasks active
        if PlaceOrder.isLock(request): return HttpResponse(PlaceOrder.errorMessage)

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

        # If there are pending tasks active
        if PlaceOrder.isLock(request): return HttpResponse(PlaceOrder.errorMessage)

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


    @staticmethod
    def isLock(request):
        if Signal.objects.filter(status='pending').count() != 0:
            return True
        else:
            return False

    # @staticmethod
    # def lock(request):
    #     # If more than one pending or new signal is in the table
    #     print('got in lock---------------------')
    #     print(Signal.objects.filter(status='pending').count())
    #
    #     if Signal.objects.filter(status='pending').count() != 0:
    #         print('got in IF true')
    #         return HttpResponse(
    #             'Error: Request is in progress. You can not send more than one request at a time.<br>'
    #             'Possible problem 1: requests are not handled with IB and no response is received form IB Gateway.<br>'
    #             'Possible problem 2: IB Gateway is not connected. Check the status in VNC.<br>' + str(
    #                 datetime.datetime.now()))



    def __delete__(self):
        return HttpResponse("")
