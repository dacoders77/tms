from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from multiprocessing import Process
import time

# sys.exit() # Python die


def fare():
    print("d1")
    for i in range(10):
        print(i)
        time.sleep(1.2)


def bare():
    for i in range(10):
        print(f"xx: {i}")
        time.sleep(2)


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def contractDetails(self, reqId, contractDetails):
        print("Contract details jojo:", reqId, " ", contractDetails)

# Main class. Entry point
def main():
    app = TestApp()
    app.connect("127.0.0.1", 4002, 0) # 7497 live

    # Crete a contract
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = "NASDAQ"
    app.reqContractDetails(1, contract)  # id, contract

    app.run() # IB app run

if __name__ == "__main__":
    process = Process(target=fare) # First parallel process
    process.start()
    #main() # IB app run. Works good
    process = Process(target=main) # Second parallel process
    process.start()
