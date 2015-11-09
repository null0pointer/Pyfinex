from consts import *

import websocket
import thread
import time
import json

class PyfinexWebsocket:
    
    def __init__(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(BFX_WEBSOCKET_ADDRESS, on_message = self.on_message, on_error = self.on_error, on_close = self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()
        
    def subscribe_book(self):
        print "subscribing to BTCUSD book"
        self.ws.send(BOOK_SUBSCRIBE_STRING);

    def subscribe_ticker(self):
        print "subscribing to BTCUSD ticker"
        self.ws.send(TICKER_SUBSCRIBE_STRING);
        
    def subscribe_trades(self):
        print "subscribing to BTCUSD trades"
        self.ws.send(TRADES_SUBSCRIBE_STRING);

    def on_message(self, ws, message):
        print message
        obj = json.loads(message);
        if (type(obj) is dict):
            if (obj[KEY_EVENT] == EVENT_SUBSCRIBED):
                channel = obj[KEY_CHANNEL_NAME]
                if (channel == "book"):
                    self.book_channel_id = obj[KEY_CHANNEL_ID];
                    print "subscribed to the orderbook"
                elif (channel == "ticker"):
                    self.ticker_channel_id = obj[KEY_CHANNEL_ID];
                    print "subscribed to the ticker"
                elif (channel == "trades"):
                    self.trades_channel_id = obj[KEY_CHANNEL_ID];
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