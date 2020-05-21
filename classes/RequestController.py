# Receives requests from urls.py
# Adds a request to DB
# Runs a loop which waits for the response to be written to DB

from django.http import HttpResponse
from classes.Request import Request
import os.path
import logging # Default logger
import json
import time
import datetime
from ib.models import Signal

#import sys
#sys.path.insert(1, 'classes/')  # Path to DbLogger.py
#//from DbLogger import DbLogger

class PlaceOrder:

    errorMessage = 'Error: Request is in progress. You can not send more than one request at a time.<br>' \
                   'Possible problem 1: No response is received form IB Gateway.<br>'\
                   'Possible problem 2: IB Gateway is not connected. Check the status in VNC.<br>' + str(datetime.datetime.now())

    @staticmethod
    def botstatus(request):
        #print("Entered botstatus")
        logging.debug("Code: xx88zz. Entered bot status") # Works good

        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "botstatus"
        })

        # Add a record to bd. Keep the whole added record in res
        res = PlaceOrder.store(requestPayload)

        # 1. Spin loop for 20 sec
        # 2. If the response is not received (record.response_payload != None) ->
        # 3. Show the current HTTP error message
        # 4. Update the same record's status to "eexpired"
        # 5. And keep on going ..

        # Wait for response from IB
        PlaceOrder.waitLoop(res)
        # Update request status to expired in no response
        PlaceOrder.update(res.id)

        # loop here. Wait 20 sec
        # for i in range(1):
        #     record = Signal.objects.get(id=res.id)
        #     print(record)
        #     if record.response_payload != None:
        #         return HttpResponse('Bot time: ' + str(datetime.datetime.now()) + '<br> Status: ' + record.response_payload)
        #     time.sleep(1)

        return HttpResponse('Bot status timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))


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

        # Add a record to bd
        res = PlaceOrder.store(requestPayload)

        # loop here. Wait 20 sec
        # for i in range(20):
        #     record = Signal.objects.get(id=res.id) # Check the created record
        #     print(record)
        #     if record.response_payload != None:
        #         return HttpResponse(
        #             'Bot time: ' + str(datetime.datetime.now()) + '<br> Status: ' + record.response_payload)
        #     time.sleep(1)

        PlaceOrder.waitLoop(res)
        PlaceOrder.update(res.id)

        return HttpResponse('Place timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))

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

        # Add a record to bd
        res = PlaceOrder.store(requestPayload)

        # loop here. Wait 20 sec
        # for i in range(20):
        #     record = Signal.objects.get(id=res.id)
        #     print(record)
        #     if record.response_payload != None:
        #         return HttpResponse('Bot time: ' + str(datetime.datetime.now()) + '<br> Quote: ' + record.response_payload)
        #     time.sleep(1)

        PlaceOrder.waitLoop(res)
        PlaceOrder.update(res.id)

        return HttpResponse(
            'Getquote status timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))

    @staticmethod
    def cancelallorders(request):

        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "cancelall"
        })

        # Add a record to bd
        res = PlaceOrder.store(requestPayload)

        # loop here. Wait 20 sec
        # for i in range(20):
        #     record = Signal.objects.get(id=res.id)
        #     print(record)
        #     if record.response_payload != None:
        #         # Return only price
        #         return HttpResponse(
        #             'Bot time: ' + str(datetime.datetime.now()) + '<br> Cancel all: ' + record.response_payload)
        #     time.sleep(1)

        PlaceOrder.waitLoop(res)
        PlaceOrder.update(res.id)

        return HttpResponse('Cancel all timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))

    @staticmethod
    def getpositions(request, symbol=""):
        # If there are pending tasks active
        if PlaceOrder.isLock(): return HttpResponse(PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "getpositions",
            "symbol": symbol
        })

        # Add a record to bd
        res = PlaceOrder.store(requestPayload)

        # loop here. Wait 20 sec
        # for i in range(20):
        #     record = Signal.objects.get(id=res.id)
        #     print(record)
        #     if record.response_payload != None:
        #         # Return only price
        #         return HttpResponse(
        #             'Bot time: ' + str(datetime.datetime.now()) + '<br> Get positions: ' + record.response_payload)
        #     time.sleep(1)

        PlaceOrder.waitLoop(res)
        PlaceOrder.update(res.id)

        return HttpResponse('Getorders timeout error. Response from the exchange has not been received within 10 seconds. ' + str(datetime.datetime.now()))

    @staticmethod
    def isLock():
        if Signal.objects.filter(status='pending').count() != 0:
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

        # Update status to expired if no response from trading script
        # Spinned the loop but no response
        if record.response_payload != None:
            PlaceOrder.update(res.id)

    # Delete. Moved to wsgi.py
    #@staticmethod
    # def SetupLogger(error):
    #     if not os.path.exists("log"):
    #         os.makedirs("log")
    #
    #     time.strftime("pyibapi.%Y%m%d_%H%M%S.log")
    #     recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    #     timefmt = '%y%m%d_%H:%M:%S'
    #
    #     logdb = DbLogger()
    #     logging.basicConfig(level=logging.DEBUG, format=recfmt, datefmt=timefmt)  # level=logging.INFO
    #     logging.getLogger('').addHandler(logdb)
    #
    #     logging.getLogger('MY_LOGGER').setLevel('DEBUG')
    #     logging.getLogger('MY_LOGGER').error(error)

    def __delete__(self):
        return HttpResponse("")
