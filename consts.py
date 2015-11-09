# API JSON KEYS

KEY_CHANNEL_NAME = "channel"
KEY_CHANNEL_ID = "chanId"
KEY_EVENT = "event"

# COMMON API JSON VALUES

EVENT_SUBSCRIBED = "subscribed"

# USEFUL STRINGS

BFX_WEBSOCKET_ADDRESS = "wss://api2.bitfinex.com:3000/ws"

BOOK_SUBSCRIBE_STRING = "{\"event\":\"subscribe\",\"channel\":\"book\",\"pair\":\"BTCUSD\",\"prec\":\"P0\"}"
TICKER_SUBSCRIBE_STRING = "{\"event\":\"subscribe\",\"channel\":\"ticker\",\"pair\":\"BTCUSD\"}"
TRADES_SUBSCRIBE_STRING = "{\"event\":\"subscribe\",\"channel\":\"trades\",\"pair\":\"BTCUSD\"}"