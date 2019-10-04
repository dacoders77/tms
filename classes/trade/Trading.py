import sys
sys.path.insert(1, 'samples/Python/Testbed') # Path to testbed
import datetime
import collections
import logging
import time
import os.path
import json
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

# Thread
import threading
# Models
from ib.models import Signal

# types
from ibapi.common import *
#from ibapi.order_condition import *
from ibapi.contract import *
from ibapi.order import *
from ibapi.order_state import *
from ibapi.execution import Execution
# from ibapi.execution import ExecutionFilter
# from ibapi.commission_report import CommissionReport
from ibapi.ticktype import *
# from ibapi.tag_value import TagValue
# from ibapi.account_summary_tags import *

from ContractSamples import ContractSamples  # Works good
from OrderSamples import OrderSamples  # Works good

sys.path.insert(1, 'classes/')  # Path to DbLogger.py
from DbLogger import DbLogger


def SetupLogger(self):
    if not os.path.exists("log"):
        os.makedirs("log")

    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")
    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    timefmt = '%y%m%d_%H:%M:%S'

    # DB logger
    # https://stackoverflow.com/questions/2314307/python-logging-to-database
    logdb = DbLogger()
    logging.basicConfig(level=logging.DEBUG, format=recfmt, datefmt=timefmt) # level=logging.INFO
    logging.getLogger('').addHandler(logdb)

    self.log.setLevel('DEBUG')
    # self.log.error('error text') # Db logger message sample
    # logging.error('error text') # Default logger message sample


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

        self.timestamp = None  # Id for reqContractDetails
        self.botStatusAwait = 0  # During this period the response must be received, otherwise - throw timeout

        self.log = logging.getLogger('MY_LOGGER')  # DB Log

    # Get the next order ID. Called automatically on startup
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        self.log.error('From nextValidID (connected successfully): ' + str(orderId))
        print("From nextValidId:", orderId)

    # Increment nextValidOrderid
    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    # Called on placeOrder
    def orderStatus(self, orderId: OrderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        response =  "OrderStatus. Id:", orderId, "Status:", status, "Filled:", filled, "Remaining:", \
                    remaining, "AvgFillPrice:", avgFillPrice, "PermId:", permId, "ParentId:", parentId,\
                    "LastFillPrice:", lastFillPrice, "ClientId:", clientId, "WhyHeld:", whyHeld, \
                    "MktCapPrice:", mktCapPrice
        print("From order status(Trading.py)" + str(response))

        # Update response field
        try:
            record = Signal.objects.get(req_id=self.nextValidOrderId)
            record.response_payload = response
            record.status = 'processed'
            record.save()
        except:
            error = 'Trading.py. Update Model query error. Most likely - no MYSQL connection. Code: 99oozz'
            print(error)
            self.log.error(error)

    # Called on reqContractDetails
    def contractDetails(self, reqId,  contractDetails: ContractDetails):
        print(f"Contract details reqId(from TWS)/DB ID: {reqId} / {self.timestamp}")
        # Update response field
        try:
            record = Signal.objects.get(req_id=self.timestamp)
            record.response_payload = 'alive'  # contractDetails.liquidHours
            record.status = 'processed'
            record.save()
        except:
            error = 'Trading.py. Update Model query error. Most likely - no MYSQL connection. Code: 99oozz2'
            print(error)
            self.log.error(error)


        self.printinstance(contractDetails)

    # Called on reqCurrentTime
    def currentTime(self, time:int):
        super().currentTime(time)
        currentTime = datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S")
        print("from currentTime(). CurrentTime:", currentTime)

    # Called on reqMktData
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        # print("TickPrice(JKJB). TickerId:", reqId, "tickType:", tickType, "Price:", price, "CanAutoExecute:", attrib.canAutoExecute,
        #      "PastLimit:", attrib.pastLimit, end=' ')
        if tickType == TickTypeEnum.BID or tickType == TickTypeEnum.ASK:
            print("PreOpen:", attrib.preOpen)

        # Get tick #68 - delayed last trade price. https://interactivebrokers.github.io/tws-api/tick_types.html
        if (tickType == 68):
            try:
                obj = Signal.objects.get(req_id=self.timestamp)
                obj.response_payload = price
                obj.status = 'processed'
                obj.save()
            except:
                error = 'Trading.py. Update Model query error. Most likely - no MYSQL connection. Code: 99oozz3'
                print(error)
                self.log.error(error)

        # CANCEL TICKS HERE?
        # Seems like ticks are still coming
        print('Trading.py def tickPrice TICKS ARE STILL COMING! WE NEED TO CANCEL SUBSCRIPTION')
        #TestApp.cancelMktData()



    # Functions not related to IB

    # Print contract details instance. Executed on reqContractDetails. Called from contractDetails
    def printinstance(self, inst: Object):
        attrs = vars(inst)
        print(', '.join("%s: %s" % item for item in attrs.items()))

    def timeStamp(self):
        t = self.timestamp = int(time.time())
        return t

    def main(self):
        # Logger settings
        SetupLogger(self)
        logging.debug("From def main. now is %s", datetime.datetime.now())
        logging.getLogger().setLevel(logging.ERROR)  # logging.INFO

        try:
            # Create IB instance and connect
            app = TestApp() # app instance created again! The first one is created in co.py! Fix this
            app.connect("127.0.0.55", 4003, 0)  # 4002 7496. 4003 - linux
            print("After connection attempt: serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))
            app.reqCurrentTime()

            # Switch to live (1) frozen (2) delayed (3) delayed frozen (4).
            app.reqMarketDataType(MarketDataTypeEnum.DELAYED)

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
    # this - context of the TestApp class
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
                    print(f"Watch loop: new record id: {record.id}")
                    rec = json.loads(record.request_payload)  # Parse json

                    if rec['url'] == 'placeorder':
                        self.app.nextOrderId()
                        contract = ContractSamples.USStock()
                        contract.exchange = rec['exchange']
                        contract.symbol = rec['symbol']
                        self.app.placeOrder(self.app.nextValidOrderId, contract, OrderSamples.MarketOrder(rec['direction'], rec['volume']))
                        print("Request payload (Trading.py placeorder):" + str(rec))
                        try:
                            record.status = "pending"
                            record.req_id = self.app.nextValidOrderId
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Most likely - no MYSQL connection. Code: 99oozz4'
                            print(error)
                            self.log.error(error)

                    if rec['url'] == 'botstatus' and record.status != 'pending':
                        self.app.timeStamp()
                        print('Entered bot status:' + str(i) + ' ' + str(self.app.timestamp))
                        contract = ContractSamples.USStock()
                        contract.exchange = 'nyse'
                        contract.symbol = 'aapl'
                        self.app.reqContractDetails(self.app.timestamp, contract)
                        try:
                            record.status = "pending"
                            record.req_id = self.app.timestamp
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Most likely - no MYSQL connection. Code: 99oozz5'
                            print(error)
                            self.log.error(error)

                    if rec['url'] == 'getquote' and record.status != 'pending':
                        self.app.timeStamp()
                        print('Entered bot get quote:' + str(i) + ' ' + str(self.app.timestamp))
                        contract = ContractSamples.USStock()
                        contract.exchange = rec['exchange']
                        contract.symbol = rec['symbol']
                        # self.app.reqContractDetails(self.app.timestamp, contract)
                        # Tick types
                        self.app.reqMktData(self.app.timestamp, contract, "", False, False, [])
                        try:
                            record.status = "pending"
                            record.req_id = self.app.timestamp
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Most likely - no MYSQL connection. Code: 99oozz6'
                            print(error)
                            self.log.error(error)

                        # https://github.com/dacoders77/tbr/blob/master/!%D1%81%23/TBR_noform/Classes/ApiManager.cs
                        # iBClient.ClientSocket.reqMktData(requestId, contract, "", true, false, null);

                        # https://github.com/dacoders77/tbr/blob/master/!%D1%81%23/TBR_noform/Form1.cs
                        # ibClient.TickPrice += IbClient_TickPrice; // reqMarketData. EWrapper Interface

                    if rec['url'] == 'cancelall' and record.status != 'pending':
                        self.app.timeStamp()
                        print('Entered cancel all:' + str(i) + ' ' + str(self.app.timestamp))
                        self.app.reqGlobalCancel()
                        try:
                            record.status = 'processed'
                            record.req_id = self.app.timestamp
                            record.response_payload = 'cancel all ok'
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Most likely - no MYSQL connection. Code: 99oozz7'
                            print(error)
                            self.log.error(error)

            time.sleep(1)