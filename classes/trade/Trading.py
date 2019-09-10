import sys
sys.path.insert(1, 'samples/Python/Testbed') # Path to testbed
import datetime
import collections
import logging
import time
import os.path

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

import threading
from ib.models import Signal

# types
from ibapi.common import *
#from ibapi.order_condition import *
from ibapi.contract import *
from ibapi.order import *
from ibapi.order_state import *
# from ibapi.execution import Execution
# from ibapi.execution import ExecutionFilter
# from ibapi.commission_report import CommissionReport
# from ibapi.ticktype import *
# from ibapi.tag_value import TagValue
#
# from ibapi.account_summary_tags import *


from ContractSamples import ContractSamples # Works good
from OrderSamples import OrderSamples # Works good

import json


def SetupLogger():
    if not os.path.exists("log"):
        os.makedirs("log")

    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")
    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    timefmt = '%y%m%d_%H:%M:%S'

    # logging.basicConfig( level=logging.DEBUG,
    #                    format=recfmt, datefmt=timefmt)
    logging.basicConfig(filename=time.strftime("log/pyibapi.%y%m%d_%H%M%S.log"),
                        filemode="w",
                        level=logging.DEBUG, # INFO
                        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logger.addHandler(console)

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.nKeybInt = 0
        self.started = False
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.reqId2nErr = collections.defaultdict(int)
        self.globalCancelOnly = False
        self.simplePlaceOid = None


    # Get the next order ID. Called automatically on startup
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        print("NextValidId(from override):", orderId)
        # Run the Function. It can be any
        self.orderOperations_req()

    # Increment nextValidOrderid
    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    def orderOperations_req(self):
        # If not check - orders will be placed consistently
        if self.started:
            return

        # Will need to set this flag to false somewhere in order to place a new order
        self.started = True

        # The parameter is always ignored.
        #self.reqIds(-1)
        #self.placeOrder(self.nextOrderId(), ContractSamples.EurGbpFx(), OrderSamples.MarketOrder("SELL", 20000))

    # Called on placeOrder
    # https://interactivebrokers.github.io/tws-api/order_submission.html
    # def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
    #
    #     #super().openOrder(orderId, contract, order, orderState)
    #
    #     print("OpenOrder(Trading.py). PermId: ", order.permId, "ClientId:", order.clientId, " OrderId:", orderId,
    #           "Account:", order.account, "Symbol:", contract.symbol, "SecType:", contract.secType,
    #           "Exchange:", contract.exchange, "Action:", order.action, "OrderType:", order.orderType,
    #           "TotalQty:", order.totalQuantity, "CashQty:", order.cashQty,
    #           "LmtPrice:", order.lmtPrice, "AuxPrice:", order.auxPrice, "Status:", orderState.status)

    # Called on placeOrder. Works good
    def orderStatus(self, orderId: OrderId, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        response =  "OrderStatus. Id:", orderId, "Status:", status, "Filled:", filled, "Remaining:", \
                    remaining, "AvgFillPrice:", avgFillPrice, "PermId:", permId, "ParentId:", parentId,\
                    "LastFillPrice:", lastFillPrice, "ClientId:", clientId, "WhyHeld:", whyHeld, \
                    "MktCapPrice:", mktCapPrice
        print("From order status(Trading.py)" + str(response))
        # Update response field
        record = Signal.objects.get(req_id=self.nextValidOrderId)
        record.response_payload = response
        record.save()


    # Called on reqContractDetails
    def contractDetails(self, reqId, contractDetails):
        print("Contract details jojo:", reqId, " ", contractDetails)

    def main(self):
        # Logger settings
        SetupLogger()
        logging.debug("now is %s", datetime.datetime.now())
        logging.getLogger().setLevel(logging.ERROR)  # logging.INFO

        try:
            app = TestApp() # app instance created again! The first one is created in co.py! Fix this
            app.connect("127.0.0.1", 4003, 0) # 4002 7496. 4003 - linux
            print("serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))

            # Crete a contract
            contract = Contract()
            contract.symbol = "AAPL"
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            contract.primaryExchange = "NASDAQ"
            #app.reqContractDetails(1, contract)  # id, contract

            # Watcher thread
            thread = MyThread(1, app, self)
            thread.start()

            # Run IB app
            app.run()

        except:
            raise


# Thread class. Use: import threading. Inherit from threading.Thread
class MyThread(threading.Thread):
    # Constructor. We pass app class instance as an argument
    # this - context of the TestApp clas
    def __init__(self, number, app, this):
        super(MyThread, self).__init__()
        self.number = number
        self.app = app
        self.this = this

    def run(self):
        i = 1
        while i == 1:
            records = Signal.objects.all()
            for record in records:
                if record.status == "new":
                    print(f"new record id: {record.id}")
                    rec = json.loads(record.request_payload) # Parse json
                    self.app.nextOrderId()

                    # STK
                    #contract = ContractSamples.USStock()
                    #contract.symbol = rec['symbol']
                    #self.app.placeOrder(self.app.nextOrderId(), contract, OrderSamples.MarketOrder(rec['direction'], rec['volume']))

                    #contract = ContractSamples.EurGbpFx()
                    contract = ContractSamples.USStock()
                    contract.symbol = rec['symbol']
                    self.app.placeOrder(self.app.nextValidOrderId, contract, OrderSamples.MarketOrder(rec['direction'], rec['volume']))

                    #print("next trading.py:" + str(self.app.nextValidOrderId))

                    print("Request payload(Trading.py):" + str(rec))

                    record.status = "processed"
                    record.url = rec['url']
                    record.req_id = self.app.nextValidOrderId
                    record.save()
                    time.sleep(1)


