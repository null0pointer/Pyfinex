from time import sleep

from pyfinex import PyfinexWebsocket

def ticker_update(bid, bid_size, ask, ask_size, daily_change, daily_change_percentage, last_price, volume, high, low):
    price_range = high - low
    price_step = price_range / 50
    last_price_string = "{:.2f}".format(last_price)
    low_price_string = "{:.2f}".format(low)
    high_price_string = "{:.2f}".format(high)
    
    price_string = low_price_string
    current = low
    dash_count = 0
    while current < last_price:
        current += price_step
        dash_count += 1
        price_string += "-"
        
    price_string += last_price_string
    for i in range(dash_count, 51):
        price_string += "-"
    price_string += high_price_string
        
    print price_string
    
def trades_update(sequence_id, timestamp, price, amount):
    buy_sold = "sold" if (amount < 0) else "bought"
    trade_string = str(timestamp) + ": " + str(abs(amount)) + " " + buy_sold + " at " + str(price)
    print trade_string

if __name__ == "__main__":
    pf = PyfinexWebsocket()
    pf.subscribe_ticker(ticker_update)
    pf.subscribe_trades(trades_update)
    
    while True:
        sleep(1)