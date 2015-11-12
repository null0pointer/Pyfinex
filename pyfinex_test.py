from time import sleep
import time

from pyfinex import PyfinexWebsocket

def ticker_update(bid, bid_size, ask, ask_size, daily_change, daily_change_percentage, last_price, volume, high, low):
    price_range = high - low
    price_step = price_range / 50
    last_price_string = "{:.2f}".format(last_price)
    low_price_string = "{:.2f}".format(low)
    high_price_string = "{:.2f}".format(high)
    
    price_string = str(int(time.time() * 1000)) + ": " + low_price_string + "-"
    current = low
    dash_count = 0
    while current < last_price:
        current += price_step
        dash_count += 1
        price_string += "-"
        
    price_string += last_price_string
    for i in range(dash_count, 50):
        price_string += "-"
    price_string += "-" + high_price_string
        
    print price_string
    
def trades_update(sequence_id, timestamp, price, amount):
    buy_sold = "sold" if (amount < 0) else "bought"
    trade_string = "trade " + str(sequence_id) + " at " + str(timestamp) + ": " + str(abs(amount)) + " " + buy_sold + " at " + str(price)
    print trade_string
    
def book_update(price, count, amount, clear):
    if not clear:
        bid_ask = "bid" if (amount > 0) else "ask"
        book_string = str(price) + " " + bid_ask + " for " + str(abs(amount)) + " BTC"
        print book_string
    else:
        print "Orderbook cleared!"

if __name__ == "__main__":
    pf = PyfinexWebsocket()
    # pf.subscribe_ticker(ticker_update)
    # pf.subscribe_trades(trades_update)
    # pf.subscribe_book(book_update)
    
    lines = [line.strip() for line in open('api.keys')]
    api_key = lines[0]
    api_secret = lines[1]
    pf.subscribe_private(api_key, api_secret)
    
    while True:
        sleep(1)