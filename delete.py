from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def contractDetails(self, reqId, contractDetails):
        print("Contract details:", reqId, " ", contractDetails)

def main():
    app = TestApp()
    app.connect("127.0.0,1", 4002, 0) # 7497 live

    app.run()


if __name__ == "__main__":
    main()