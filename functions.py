from math import floor
import alpaca_trade_api as tradeapi
from alpaca_trade_api import StreamConn, REST
import requests
import asyncio
import json

API_KEY="PK90ZGBIDL4SPDOQNWEV"
API_SECRET_KEY="Fxx8vj0KZlZnWUGbFdSxOSuuAWAJA9hPALXJGYuZ"

HEADERS = {'APCA-API-KEY-ID': API_KEY,
           'APCA-API-SECRET-KEY': API_SECRET_KEY}
DATA_URL = 'https://data.alpaca.markets'

base_url= "https://paper-api.alpaca.markets"
ALPACA_BASE_URL=base_url

rest_api= REST(API_KEY, API_SECRET_KEY, base_url)

waitTime = 10
min_arb_percent = 0.001


prices = {
    'ETH/USD' : 1,
    'BTC/USD' : 1,
    'ETH/BTC' : 1
}


async def get_quote(symbol: str):
    '''
    Get quote data from Alpaca API
    '''
 
    try:
        # make the request
            quote = requests.get('{0}/v1beta2/crypto/latest/trades?symbols={1}'.format(DATA_URL, symbol), headers=HEADERS)
            prices[symbol] = quote.json()['trades'][symbol]['p']
            print(f'prices', prices)
            # Status code 200 means the request was successful
            if quote.status_code != 200:
                print("Undesirable response from Alpaca! {}".format(quote.json()))
                return False
 
    except Exception as e:
        print("There was an issue getting trade quote from Alpaca: {0}".format(e))
        return False

def post_Alpaca_order(symbol, qty, side):
    '''
    Post an order to Alpaca
    '''
    try:
        order = requests.post(
            '{0}/v2/orders'.format(ALPACA_BASE_URL), headers=HEADERS, json={
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': 'market',
                'time_in_force': 'gtc',
            })
        print(f'post_order', order)
        return order
    except Exception as e:
        print("There was an issue posting order to Alpaca: {0}".format(e))
        return False


async def check_arb():
    '''
    Check to see if an arbitrage condition exists
    '''    

    ETH = prices['ETH/USD']
    BTC = prices['BTC/USD']
    ETHBTC = prices['ETH/BTC']
    DIV = ETH / BTC
    spread = abs(DIV - ETHBTC)
    BUY_ETH = 10000 / ETH
    BUY_BTC = 10000 / BTC
    BUY_ETHBTC = BUY_BTC / ETHBTC

    SELL_ETHBTC = BUY_ETH / ETHBTC

    print(BUY_BTC,BUY_ETHBTC, 1/BUY_ETHBTC )

    print(SELL_ETHBTC)
    spreads=[]

# when BTC/USD is cheaper
    if DIV > ETHBTC * (1 + min_arb_percent/100):
        print('STRATEGY 1')
        #from USD to BTC
        order1 = post_Alpaca_order("BTCUSD", BUY_BTC, "buy")
        if order1.status_code == 200:
            #from BTC to ETH
            order2 = post_Alpaca_order("ETH/BTC", BUY_ETHBTC, "buy")
            print(f'order 2',order2._content, BUY_ETHBTC)
            if order2.status_code == 200:
                #from ETH to USD
                order3 = post_Alpaca_order("ETHUSD", BUY_ETHBTC, "sell")
                print(f'order 3',order3.content, BUY_ETHBTC)
                if order3.status_code == 200:
                    print("Done (type 1) eth: {} btc: {} ethbtc {}".format(ETH, BTC, ETHBTC))
                    print("Spread: +{}".format(abs(spread) * 100))
                else:
                    post_Alpaca_order("ETH/BTC", BUY_ETHBTC, "sell")
                    print("Bad Order 3")
                    exit()
            else:
                post_Alpaca_order("BTCUSD", BUY_BTC, "sell")
                print("Bad Order 2")
                exit()
        else:
            print("Bad Order 1")
            exit()
 
    # when ETH/USD is cheaper
    elif DIV < ETHBTC * (1 - min_arb_percent/100):
        print('STRATEGY 2')
        #from USD to ETH
        order1 = post_Alpaca_order("ETHUSD", BUY_ETH, "buy")
        if order1.status_code == 200:
            #from ETH to BTC
            order2 = post_Alpaca_order("ETH/BTC", BUY_ETH, "sell")
            print(f'order 2',order2.content)
            if order2.status_code == 200:
                order3 = post_Alpaca_order("BTCUSD", BUY_BTC, "sell")
                print(f'order 3',order3.content)
                if order3.status_code == 200:
                    print("Done (type 2) eth: {} btc: {} ethbtc {}".format(ETH, BTC, ETHBTC))
                    print("Spread: -{}".format(spread * 100))
                else:
                    post_Alpaca_order("ETH/BTC", SELL_ETHBTC, "buy")  
                    print("Bad Order 3")                
                    exit()
            else:
                post_Alpaca_order("ETHUSD", BUY_ETH, "sell")
                print("Bad Order 2")
                exit()    
        else:
            print("Bad order 1")
            exit()
    else:
        print("No arb opportunity, spread: {}".format(spread * 100))
        spreads.append(spread)



def get_account_data():
    account=rest_api.get_account
    cash=account
    return cash
