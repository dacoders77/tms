import sys
sys.path.insert(1, '../..') # Path to ibapi from the current location of the script
sys.path.insert(1, '../../samples/Python/Testbed') # Path to testbed

import argparse
import datetime
import collections
import inspect

import logging
import time
import os.path

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

# types
# from ibapi.common import * # @UnusedWildImport
# from ibapi.order_condition import * # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
# from ibapi.order import * # @UnusedWildImport
# from ibapi.order_state import * # @UnusedWildImport
# from ibapi.execution import Execution
# from ibapi.execution import ExecutionFilter
# from ibapi.commission_report import CommissionReport
# from ibapi.ticktype import * # @UnusedWildImport
# from ibapi.tag_value import TagValue
#
# from ibapi.account_summary_tags import *
#
from ContractSamples import ContractSamples # Works good
from OrderSamples import OrderSamples # Works good

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
                        #level=logging.INFO,
                        level=logging.DEBUG,
                        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logger.addHandler(console)


class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        # ! [socket_init]
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
        print("NextValidId:", orderId)
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
        self.reqIds(-1)
        self.placeOrder(self.nextOrderId(), ContractSamples.EurGbpFx(),
                        OrderSamples.MarketOrder("SELL", 20000))

    # Called on reqContractDetails
    def contractDetails(self, reqId, contractDetails):
        print("Contract details jojo:", reqId, " ", contractDetails)


def main():
    SetupLogger()
    logging.debug("now is %s", datetime.datetime.now())
    logging.getLogger().setLevel(logging.ERROR) # logging.INFO

    try:
        app = TestApp()
        app.connect("127.0.0.1", 4002, 0)
        print("serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))

        # Crete a contract
        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"
        # app.reqContractDetails(1, contract)  # id, contract

        app.run()

    except:
        raise


if __name__ == "__main__":
    main()