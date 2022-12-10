import alpaca_trade_api as tradeapi
from alpaca_trade_api import  REST
import requests
import asyncio
from functions import get_quote, check_arb, waitTime, rest_api, get_account_data

from tradingview import get_coin_tickers, collect_tradeables, structure_triangular_pairs, get_price_for_t_pair, check_arbitrage, calc_triangular_arb_surface_rate
import json
import time


min_arb_percent=0.3

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


async def main2():
    structured_pairs= open_trading_pairs()
    # Get Latest Surface Prices
    # Loop Through and Structure Price Information
    while True:
        for t_pair in structured_pairs:

            task1, quotes_base = await get_price_for_t_pair(t_pair)

            task2 = await check_arbitrage(task1)
            if task2 == True: 
                calc_triangular_arb_surface_rate(quotes_base, task1)

                




"""async def main2():
        while True:
            task= loop.create_task(step_2())
            await asyncio.wait([task])
            print(f'main', task)
"""

loop = asyncio.get_event_loop()
loop.run_until_complete(main2())
loop.close()




"""
        pair_1=get_quote(t_pair['pair_a'])
        pair_2=get_quote(t_pair['pair_b'])
        pair_3= get_quote(t_pair['pair_c'])"""
"""
        print(pair_2)

        time.sleep(0.3)
        prices_dict = get_price_for_t_pair(t_pair, prices_json)
        surface_arb = calc_triangular_arb_surface_rate(t_pair, prices_dict)
        if len(surface_arb) > 0:
            print(surface_arb)
        else: 
            print("Fanculo")
            real_rate_arb = get_depth_from_orderbook(surface_arb)
            print(real_rate_arb, time.time)
            time.sleep(1)

            return(real_rate_arb)
"""


def orders(real_rate_arb):
    if real_rate_arb is not None:
        symbol = real_rate_arb['contract_1'].split("_")
        coin1= symbol[0]+symbol[1]
        market_price1 = rest_api.get_latest_crypto_quote(coin1, exchange="FTXU").close
        print(market_price1)
        return coin1, market_price1



    rest_api.close_all_positions()
    available_cash = float(rest_api.get_account().cash)
    print(available_cash)
    percent=0.1