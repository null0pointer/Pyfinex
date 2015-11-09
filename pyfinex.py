import websocket
import thread
import time
import json

class PyfinexWebsocket:
    
    BOOK_SUBSCRIBE_STRING = "{\"event\":\"subscribe\",\"channel\":\"book\",\"pair\":\"BTCUSD\",\"prec\":\"P0\"}"
    TICKER_SUBSCRIBE_STRING = "{\"event\":\"subscribe\",\"channel\":\"ticker\",\"pair\":\"BTCUSD\"}"
    TRADES_SUBSCRIBE_STRING = "{\"event\":\"subscribe\",\"channel\":\"trades\",\"pair\":\"BTCUSD\"}"
    
    def __init__(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://api2.bitfinex.com:3000/ws", on_message = self.on_message, on_error = self.on_error, on_close = self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()
        
    def subscribe_book(self):
        print "subscribing to BTCUSD book"
        self.ws.send(PyfinexWebsocket.BOOK_SUBSCRIBE_STRING);

    def subscribe_ticker(self):
        print "subscribing to BTCUSD ticker"
        self.ws.send(PyfinexWebsocket.TICKER_SUBSCRIBE_STRING);
        
    def subscribe_trades(self):
        print "subscribing to BTCUSD trades"
        self.ws.send(PyfinexWebsocket.TRADES_SUBSCRIBE_STRING);

    def on_message(self, ws, message):
        print message
        obj = json.loads(message);
        if (type(obj) is dict):
            if (obj["event"] == "subscribed"):
                channel = obj["channel"]
                if (channel == "book"):
                    print "subscribed to the orderbook"
                elif (channel == "ticker"):
                    print "subscribed to the ticker"
                elif (channel == "trades"):
                    print "subscribed to the trades"

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        print "### closed ###"

    def on_open(self, ws):
        self.subscribe_book()
        self.subscribe_ticker()
        self.subscribe_trades()

if __name__ == "__main__":
    pf = PyfinexWebsocket()