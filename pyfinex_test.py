from time import sleep

from pyfinex import PyfinexWebsocket

if __name__ == "__main__":
    pf = PyfinexWebsocket()
    pf.subscribe_ticker();
    
    while True:
        sleep(1)