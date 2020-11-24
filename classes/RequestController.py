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
import types
#
def jflush(success, msg=None):

    # Function for parsing json
    def is_json(text):
        try:
            if isinstance(text, bool):
                return False
            json_object = json.loads(text)
        except ValueError as e:
            return False
        return json_object

    # Get number of arguments
    argc = len(locals())

    # Decode json, if need
    if is_json(success): success = is_json(success)

    # Make sure success and time will be at the beginning
    flush = {'success': None, 'time': str(datetime.datetime.now())}

    # Start building data for flushing
    flush.update(success if isinstance(success, dict) and 'success' in success else {'success': True, 'response': success})

    # Deal with 2nd-argument, if given
    if argc > 1 and msg != None:
        flush.update(msg if isinstance(msg, dict) else {'response': msg})

    # Flush json-response
    return HttpResponse(json.dumps(flush), content_type=json)

class PlaceOrder:

    errorMessage = 'Error: Request in progress'
    timeOutMessage = "Bot status timeout error. Response from the exchange has not been received within 10 seconds."

    @staticmethod
    def botstatus(request):
        logging.debug("Entered bot status. Code: xx88zz.")

        # If there are pending tasks active
        if PlaceOrder.isLock(): return jflush(False, PlaceOrder.errorMessage)

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
        if PlaceOrder.isLock(): return jflush(False, PlaceOrder.errorMessage)

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
        if PlaceOrder.isLock(): return jflush(False, PlaceOrder.errorMessage)

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
        if PlaceOrder.isLock(): return jflush(False, PlaceOrder.errorMessage)

        requestPayload = json.dumps({
            "url": "cancelall"
        })

        res = PlaceOrder.store(requestPayload)
        return PlaceOrder.waitLoop(res)

    @staticmethod
    def getpositions(request, symbol=""):
        # If there are pending tasks active
        if PlaceOrder.isLock(): return jflush(False, PlaceOrder.errorMessage)

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
                # return HttpResponse('Bot time: ' + str(datetime.datetime.now()) + '<br> Payload: ' + record.response_payload)
                return jflush(record.response_payload)
            time.sleep(1)

        PlaceOrder.update(res.id)
        return jflush(False, PlaceOrder.timeOutMessage)

    def __delete__(self):
        return HttpResponse("")
