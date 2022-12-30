import alpaca_trade_api as tradeapi
from alpaca_trade_api import  REST
import requests
import asyncio
from functions import get_quote, check_arb, waitTime, rest_api
from tradingview import get_coin_tickers, collect_tradeables, structure_triangular_pairs, get_price_for_t_pair, check_arbitrage, calc_triangular_arb_surface_rate
import json
import time




def step_0():
    coin_json = get_coin_tickers()
    coin_list=collect_tradeables(coin_json)
    structured_list=structure_triangular_pairs(coin_list)
    tradable_pairs=[]
    for t_pair in structured_list:
        if t_pair['a_base'] == 'USD' or t_pair['a_quote'] == "USD": 
            if t_pair['c_base'] == 'USD' or t_pair['c_quote']== "USD":

                tradable_pairs.append(t_pair)
    # Save structured list
    with open("tradable_pairs.json", "w") as fp:
        json.dump(tradable_pairs, fp)


#open the file 
def open_trading_pairs():
    with open("tradable_pairs.json") as json_file:
        structured_pairs = json.load(json_file)
    return structured_pairs

min_arb=0.005
starting_amount= 1000


async def main2():
    structured_pairs= open_trading_pairs()
    # Get Latest Surface Prices
    # Loop Through and Structure Price Information
    while True:
        for t_pair in structured_pairs:
            print(t_pair)
            task1, quotes_base = await get_price_for_t_pair(t_pair)


            task2 = check_arbitrage(task1, min_arb)
            print(task2)
            if task2 is True: 
                calc_triangular_arb_surface_rate(quotes_base, task1, starting_amount)
            else:
                None
                #await asyncio.sleep(waitTime)


loop = asyncio.get_event_loop()
asyncio.run(main2())
loop.close()
