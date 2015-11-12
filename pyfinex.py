from consts import *

import websocket
import thread
import threading
import time
from time import sleep
import json
import hmac
import hashlib

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
        
    def subscribe_book(self, callback):
        print "subscribing to BTCUSD book"
        self.ws.send(BOOK_SUBSCRIBE_STRING);
        self.book_callback = callback

    def subscribe_ticker(self, callback):
        print "subscribing to BTCUSD ticker"
        self.ws.send(TICKER_SUBSCRIBE_STRING);
        self.ticker_callback = callback
        
    def subscribe_trades(self, callback):
        print "subscribing to BTCUSD trades"
        self.ws.send(TRADES_SUBSCRIBE_STRING);
        self.trades_callback = callback
        
    def subscribe_private(self, api_key, api_secret, callbacks):
        ### JS authentication example from API docs ###
#         var
#             crypto = require('crypto'),
#             api_key = 'API_KEY',
#             api_secret = 'API_SECRET',
#             payload = 'AUTH' + (new Date().getTime()),
#             signature = crypto.createHmac("sha384", api_secret).update(payload).digest('hex');
#         w.send(JSON.stringify({
#             event: "auth",
#             apiKey: api_key,
#             authSig: signature,
#             authPayload: payload
#         }));

        payload = "AUTH" + str(int(time.time() * 1000))
        signature = hmac.new(api_secret, payload, hashlib.sha384).hexdigest()
        auth_request = json.dumps({"event": "auth", "apiKey": api_key, "authSig": signature, "authPayload": payload})
        
        if (self.debug):
            print "API Key: " + api_key
            print "Signature Payload: " + payload
            print "Signature: " + signature
            print auth_request
            
        self.ws.send(auth_request)
        
    def __update_book(self, update_object):
        if (self.debug):
            print update_object
            
        if (hasattr(self, "book_callback")):
            price = update_object[0]
            count = update_object[1]
            amount = update_object[2]
            self.book_callback(price, count, amount, False)
        
    def __parse_book_message(self, message_object):
        if (len(message_object) > 1):
            if (type(message_object[1]) is list):
                book_updates = message_object[1]
                
                if (hasattr(self, "book_callback")):
                    self.book_callback(None, None, None, True)
                
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
                
    def __update_private_wallet(self, update_object):
        if (self.debug):
            print update_object
            
        if (hasattr(self, "private_wallet_callback")):
            name = update_object[0]
            currency = update_object[1]
            balance = update_object[2]
            unsettled_interest = update_object[3]
            self.private_wallet_callback(name, currency, balance, unsettled_interest)
            
    def __update_private_position(self, update_object):
        if (self.debug):
            print update_object
            
        if (hasattr(self, "private_position_callback")):
            pair = update_object[0]
            status = update_object[1]
            amount = update_object[2]
            base_price = update_object[3]
            margin_funding = update_object[4]
            margin_funding_type = update_object[5]
            self.private_position_callback(pair, status, amount, base_price, margin_funding, margin_funding_type)
            
    def __update_private_order(self, update_object):
        if (self.debug):
            print update_object
            
        if (hasattr(self, "private_order_callback")):
            order_id = update_object[0]
            pair = update_object[1]
            amount = update_object[2]
            original_amount = update_object[3]
            order_type = update_object[4]
            status = update_object[5]
            price = update_object[6]
            price_average = update_object[7]
            created_at = update_object[8]
            notify = update_object[9]
            hidden = update_object[10]
            self.private_order_callback(order_id, pair, amount, original_amount, order_type, status, price, price_average, created_at, notify, hidden)
                
    def __parse_private_message(self, message_object):
        print message_object
        message_object.pop(0)
        message_type = message_object.pop(0)
        
        if (message_type == "ws"):
            for update_object in message_object[0]:
                self.__update_private_wallet(update_object)
        elif (message_type == "wu"):
            update_object = message_object[0]
            self.__update_private_wallet(update_object)
        elif (message_type == "ps"):
            for update_object in message_object[0]:
                self.__update_private_position(update_object)
        elif (message_type == "pn" or message_type == "pu" or message_type == "pc"):
            update_object = message_object[0]
            self.__update_private_position(update_object)
        elif (message_type == "os"):
            for update_object in message_object[0]:
                self.__update_private_order(update_object)
        elif (message_type == "on" or message_type == "ou" or message_type == "oc"):
            update_object = message_object[0]
            self.__update_private_order(update_object)
        elif (message_type == "ts"):
            pass
        elif (message_type == "te"):
            pass
        elif (message_type == "tu"):
            pass

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
                elif (obj[KEY_EVENT] == "auth"):
                    status = obj["status"]
                    if (status == "OK"):
                        # should always be channel id 0
                        self.private_channel_id = obj[KEY_CHANNEL_ID]
                    elif (status == "FAIL"):
                        # should throw exception here
                        print "Error: " + obj["code"]
                        
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
                if (hasattr(self, "private_channel_id")):
                    if (channel_id == self.private_channel_id):
                        self.__parse_private_message(obj)

    def __on_error(self, ws, error):
        print error

    def __on_close(self, ws):
        print "### closed connection to " + BFX_WEBSOCKET_ADDRESS + " ###"

    def __on_open(self, ws):
        print "### opened connection to " + BFX_WEBSOCKET_ADDRESS + " ###"