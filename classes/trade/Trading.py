import sys
import urllib.request
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
    # Static member. Assigned in MyThread - getpositions
    positionSymbol = ""

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

        self.positionsDict = {}

    # Get the next order ID. Called automatically on startup. If this method is not called - there is no connection
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
        # response =  "OrderStatus. Id:", orderId, "Status:", status, "Filled:", filled, "Remaining:", \
        #             remaining, "AvgFillPrice:", avgFillPrice, "PermId:", permId, "ParentId:", parentId,\
        #             "LastFillPrice:", lastFillPrice, "ClientId:", clientId, "WhyHeld:", whyHeld, \
        #             "MktCapPrice:", mktCapPrice

        response = json.dumps(
            {
                "time": str(datetime.datetime.now()),
                "OrderStatus. Id:": orderId,
                "Status:": status,
                "Filled:": filled,
                "Remaining:": remaining,
                "AvgFillPrice:": avgFillPrice,
                "PermId:": permId,
                "ParentId:": parentId,
                "LastFillPrice:": lastFillPrice,
                "ClientId:": clientId,
                "WhyHeld:": whyHeld,
                "MktCapPrice:": mktCapPrice
        })

        print("From order status(Trading.py)" + str(response))

        # Update response field
        try:
            record = Signal.objects.get(req_id=self.nextValidOrderId)
            record.response_payload = response
            record.status = 'processed'
            record.order_status = status
            record.save()

            # If order status is "Filled"
            if record.order_status == "Filled":

                # Load request payload
                pl = json.loads(record.request_payload)

                # Build url
                url = 'https://connect.pabbly.com/workflow/sendwebhookdata/IjI1ODU5Ig_3D_3D/?' + urllib.parse.urlencode({
                    'ticker': pl['symbol'],
                    'direction': pl['direction'],
                    'currency': pl['currency'],
                    'volume': pl['volume'],
                })

                # Make request
                urllib.request.urlopen(url).read()

        except:
            error = 'Trading.py. Record req_id=' + self.nextValidOrderId + ' not found'
            print(error)
            self.log.error(error)

    # Called on reqContractDetails. Botstatus
    def contractDetails(self, reqId,  contractDetails: ContractDetails):
        print(f"Contract details reqId(from TWS)/DB ID: {reqId} / {self.timestamp}")
        # Update response field
        try:
            record = Signal.objects.get(req_id=self.timestamp)
            record.response_payload = json.dumps({
                "success": True,
                "response": "alive"
            })
            record.status = 'processed'
            record.save()
        except:
            error = 'Trading.py. Update Model query error. Code: 78kkpp'
            print(error)
            self.log.error(error)

        self.printinstance(contractDetails)

    # Called from reqPositions / Not used?
    def position(self, reqId, account:str, contract:Contract, position:float):
        print(f"Positions reqId(from TWS)/DB ID: {reqId} / {self.timestamp}")
        # Update response field
        try:
            record = Signal.objects.get(req_id=self.timestamp)
            record.response_payload = 'reqPosition'  # contractDetails.liquidHours
            record.status = 'processed'
            record.save()
        except:
            error = 'Trading.py. Update Model query error. Code: 99uuyy5'
            print(error)
            self.log.error(error)

        #self.printinstance(contract)
        print("position worked: ")
        print(account)
        print(contract) # + " " + contract.secType + " " + contract.exchange + " " + contract.currency

    # Called from reqPositionsMulti / Get positions
    # Will be executed several times is more than one position
    def positionMulti(self, reqId: int, account: str, modelCode: str, contract: Contract, pos: float, avgCost: float):
        super().positionMulti(reqId, account, modelCode, contract, pos, avgCost)
        print("PositionMulti event. RequestId:", reqId, "Account:", account,
              "ModelCode:", modelCode, "Symbol:", contract.symbol, "SecType:",
              contract.secType, "Currency:", contract.currency, ",Position:",
              pos, "AvgCost:", avgCost)
        # Add a position to dictionary Symbol/Volume
        self.positionsDict[contract.symbol] = pos

    # When reqPositionsMulty finishes sending events, this is the final event
    def positionMultiEnd(self, reqId: int):
        super().positionMultiEnd(reqId)
        print("PositionMultiEnd. Finished sending positions. RequestId:", reqId)

        if self.positionSymbol in self.positionsDict.keys():
            print('Position volume: ' + str(self.positionsDict[self.positionSymbol]))
            positionVolume = json.dumps({
                'success': True,
                'response': int(self.positionsDict[self.positionSymbol]) # Get rid of decimal places
            })
        else:
            positionVolume = json.dumps({
                'success': False,
                'response': 0
            })
            print(positionVolume)
            # If no symbol specified - output the whole dictionary
            positionVolume = positionVolume if self.positionSymbol != "" else self.positionsDict

        # print('Position volume payload(trace): ' + str(positionVolume))
        # print('Timestamp trace: ' + str(self.timestamp))
        # print('Signals table trace: ' + str(Signal.objects.values('id', 'req_id', 'status', 'url')))
        # print('Get DB record trace: ' + str(Signal.objects.get(req_id=self.timestamp)))

        # Update response field
        try:
            record = Signal.objects.get(req_id=self.timestamp)
            record.response_payload = positionVolume
            record.status = 'processed'
            record.save()
        except:
            error = 'Trading.py. Update Model query error. Code: 99yjjj'
            print(error)
            self.log.error(error)

    # Called on reqCurrentTime
    def currentTime(self, time:int):
        super().currentTime(time)
        currentTime = datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S")
        print("from currentTime(). CurrentTime:", currentTime)

    # Called on reqMktData / Get quote
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        #print("TickPrice(JKJB). TickerId:", reqId, "tickType:", tickType, "Price:", price, "CanAutoExecute:", attrib.canAutoExecute, "PastLimit:", attrib.pastLimit, end=' ')
        if tickType == TickTypeEnum.BID or tickType == TickTypeEnum.ASK:
            print("PreOpen:", attrib.preOpen)

        # Get tick #68 - delayed last trade price. https://interactivebrokers.github.io/tws-api/tick_types.html
        if (tickType == 68):
            TestApp.cancelMktData(self, reqId) # Cancel subscription when tick type 68 received
            try:
                obj = Signal.objects.get(req_id=self.timestamp)
                obj.response_payload = json.dumps({
                    "success": True,
                    "response": price
                })
                obj.status = 'processed'
                obj.save()
            except:
                error = 'Trading.py. Update Model query error. Code: 99oozz3'
                print(error)
                self.log.error(error)

        print('Trading.py def tickPrice. Tick received. TickerID / TickType: ' + str(reqId) + " " + str(tickType))


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
        logging.debug("Trading.py. From def main. now is %s", datetime.datetime.now())
        logging.getLogger().setLevel(logging.ERROR)  # logging.INFO

        try:
            # Create IB instance and connect
            app = TestApp() # app instance created again! The first one is created in co.py! Fix this

            # Do not change this configuration. Just change port numbers in the IBGate or TWS
            # 4003 is the default port number used in the docker container
            #app.connect("127.0.0.55", 7496, 0)  # 4002 7496. 4003 - linux

            app.connect("127.0.0.55", 4003, 0)

            print("After connection attempt: serverVersion: %s connectionTime: %s" % (app.serverVersion(), app.twsConnectionTime()))
            app.reqCurrentTime()

            # Switch to live (1) frozen (2) delayed (3) delayed frozen (4).
            app.reqMarketDataType(MarketDataTypeEnum.DELAYED)
            # app.reqMarketDataType(MarketDataTypeEnum.REALTIME)

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

                    # Place order
                    if rec['url'] == 'placeorder':
                        self.app.nextOrderId()
                        contract = ContractSamples.USStock()
                        contract.exchange = rec['exchange']
                        contract.symbol = rec['symbol']
                        contract.currency = rec['currency']

                        if rec['order_type'] == 'market':
                            # Place market orders
                            self.app.placeOrder(self.app.nextValidOrderId, contract, OrderSamples.MarketOrder(rec['direction'], rec['volume']))
                        else:
                            self.app.placeOrder(self.app.nextValidOrderId, contract, OrderSamples.LimitOrder(rec['direction'], rec['volume'], rec['price']))

                        print("Request payload (Trading.py placeorder):" + str(rec))
                        try:
                            record.status = "pending"
                            record.req_id = self.app.nextValidOrderId
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Code: 99oozz4'
                            print(error)
                            self.log.error(error)

                    # Bot status
                    if rec['url'] == 'botstatus' and record.status != 'pending':
                        self.app.timeStamp()
                        print('Entered bot status: ' + str(i) + ' ' + str(self.app.timestamp))
                        contract = ContractSamples.USStock()
                        contract.exchange = 'nyse'
                        contract.symbol = 'aapl'
                        self.app.reqContractDetails(self.app.timestamp, contract)
                        #self.app.reqPositionsMulti(self.app.timestamp, "", "")
                        try:
                            record.status = "pending"
                            record.req_id = self.app.timestamp
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Code: 99oozz5'
                            print(error)
                            self.log.error(error)

                    # Get all positions. Can be executed with symbol as an optional parameter
                    # Response will be returned to positionMulti. positionMultiEnd - will be the finalizing event
                    # https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a4fa2744c3459f9f6cf695980267608c3
                    if rec['url'] == 'getpositions' and record.status != 'pending':
                        self.app.timeStamp()
                        print('Entered bot getpositions:' + str(self.app.timestamp))
                        TestApp.positionSymbol = rec['symbol'].upper()
                        try:
                            record.status = "pending"
                            record.req_id = self.app.timestamp
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Code: 26ooutt'
                            print(error)
                            self.log.error(error)

                        self.app.reqPositionsMulti(self.app.timestamp, "", "")

                    # Get quote
                    if rec['url'] == 'getquote' and record.status != 'pending':
                        self.app.timeStamp()
                        print('Entered bot get quote:' + str(self.app.timestamp))
                        contract = ContractSamples.USStock()
                        contract.exchange = rec['exchange']
                        contract.symbol = rec['symbol']
                        contract.currency = rec['currency']
                        try:
                            record.status = "pending"
                            record.req_id = self.app.timestamp
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. On GetQuote. Code: 99oozz6'
                            print(error)
                            self.log.error(error)

                        # self.app.reqContractDetails(self.app.timestamp, contract)
                        # tickerId, contract, ticks list, snapshot, snapshot, list
                        # https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a7a19258a3a2087c07c1c57b93f659b63
                        self.app.reqMktData(self.app.timestamp, contract, "", False, False, [])

                        # https://github.com/dacoders77/tbr/blob/master/!%D1%81%23/TBR_noform/Classes/ApiManager.cs
                        # iBClient.ClientSocket.reqMktData(requestId, contract, "", true, false, null);

                        # https://github.com/dacoders77/tbr/blob/master/!%D1%81%23/TBR_noform/Form1.cs
                        # ibClient.TickPrice += IbClient_TickPrice; // reqMarketData. EWrapper Interface

                    # Cancel all
                    if rec['url'] == 'cancelall' and record.status != 'pending':
                        self.app.timeStamp()
                        print('Entered cancel all:' + str(i) + ' ' + str(self.app.timestamp))
                        self.app.reqGlobalCancel()
                        try:
                            record.status = 'processed'
                            record.req_id = self.app.timestamp
                            record.response_payload = json.dumps(
                                {
                                    "time": str(datetime.datetime.now()),
                                    "response": "cancel all ok"
                                })
                            record.save()
                        except:
                            error = 'Trading.py. Update Model query error. Code: 99oozz7'
                            print(error)
                            self.log.error(error)

            time.sleep(1)