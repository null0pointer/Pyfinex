from consts import *

import websocket
import thread
import threading
import time
from time import sleep
import json

class PyfinexWebsocket:
    
    def __init__(self, debug = False):
        self.debug = debug
        if (self.debug):
            websocket.enableTrace(True)
            
        self.ws = websocket.WebSocketApp(BFX_WEBSOCKET_ADDRESS, on_message = self.__on_message, on_error = self.__on_error, on_close = self.__on_close)
        self.ws.on_open = self.__on_open
        self.wst = threading.Thread(target = self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()
        
        # block main thread for at most 5 seconds or until websocket is connected
        connection_timeout = 5
        while not self.ws.sock.connected and connection_timeout:
                sleep(1)
                connection_timeout -= 1
        
    def subscribe_book(self):
        print "subscribing to BTCUSD book"
        self.ws.send(BOOK_SUBSCRIBE_STRING);

    def subscribe_ticker(self, callback):
        print "subscribing to BTCUSD ticker"
        self.ws.send(TICKER_SUBSCRIBE_STRING);
        self.ticker_callback = callback
        
    def subscribe_trades(self, callback):
        print "subscribing to BTCUSD trades"
        self.ws.send(TRADES_SUBSCRIBE_STRING);
        self.trades_callback = callback
        
    def __update_book(self, update_object):
        if (self.debug):
            print update_object
        
    def __parse_book_message(self, message_object):
        if (len(message_object) > 1):
            if (type(message_object[1]) is list):
                book_updates = message_object[1]
                # todo: zero out the book because this is a snapshot
                for update_object in book_updates:
                    self.__update_book(update_object)
            else:
                message_object.pop(0)
                self.__update_book(message_object)
    
    def __update_ticker(self, update_object):
        if (self.debug):
            print update_object
            
        if (hasattr(self, "ticker_callback")):
            bid = update_object[0]
            bid_size = update_object[1]
            ask = update_object[2]
            ask_size = update_object[3]
            daily_change = update_object[4]
            daily_change_percentage = update_object[5]
            last_price = update_object[6]
            volume = update_object[7]
            high = update_object[8]
            low = update_object[9]
            self.ticker_callback(bid, bid_size, ask, ask_size, daily_change, daily_change_percentage, last_price, volume, high, low)
        
    def __parse_ticker_message(self, message_object):
        message_object.pop(0)
        if (len(message_object) == 10):
            self.high = message_object[8]
            self.low = message_object[9]
            self.__update_ticker(message_object)
        elif (len(message_object) == 8):
            last_price = message_object[6]
            if (hasattr(self, "high")):
                if (last_price > self.high):
                    self.high = last_price
            else:
                self.high = last_price
                
            if (hasattr(self, "low")):
                if (last_price < self.low):
                    self.low = last_price
            else:
                self.low = last_price
                
            message_object.append(self.high)
            message_object.append(self.low)
            self.__update_ticker(message_object)
    
    def __update_trades(self, update_object):
        if (self.debug):
            print update_object
            
        if (hasattr(self, "trades_callback")):
            sequence_id = update_object[0]
            timestamp = update_object[1]
            price = update_object[2]
            amount = update_object[3]
            self.trades_callback(sequence_id, timestamp, price, amount)
        
    def __parse_trades_message(self, message_object):
        if (len(message_object) > 1):
            if (type(message_object[1]) is list):
                trade_updates = message_object[1]
                for update_object in trade_updates:
                    self.__update_trades(update_object)
            else:
                message_object.pop(0)
                self.__update_trades(message_object)

    def __on_message(self, ws, message):
        obj = json.loads(message);
        
        if (type(obj) is dict):
            if KEY_EVENT in obj.keys():
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
                        
        elif (type(obj) is list):
            if (len(obj) > 0):
                channel_id = obj[0]
                if (hasattr(self, "book_channel_id")):
                    if (channel_id == self.book_channel_id):
                        self.__parse_book_message(obj)
                if (hasattr(self, "ticker_channel_id")):
                    if (channel_id == self.ticker_channel_id):
                        self.__parse_ticker_message(obj)
                if (hasattr(self, "trades_channel_id")):
                    if (channel_id == self.trades_channel_id):
                        self.__parse_trades_message(obj)

    def __on_error(self, ws, error):
        print error

    def __on_close(self, ws):
        print "### closed connection to " + BFX_WEBSOCKET_ADDRESS + " ###"

    def __on_open(self, ws):
        print "### opened connection to " + BFX_WEBSOCKET_ADDRESS + " ###"