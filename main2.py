import alpaca_trade_api as tradeapi
from alpaca_trade_api import  REST
import requests
import asyncio
from functions import get_quote, check_arb, waitTime, rest_api, get_account_data

from tradingview import get_coin_tickers, collect_tradeables, structure_triangular_pairs, get_price_for_t_pair, calc_triangular_arb_surface_rate
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

def step_2():

    # Get Structured Pairs
    with open("tradable_pairs.json") as json_file:
        structured_pairs = json.load(json_file)

    # Get Latest Surface Prices
    # Loop Through and Structure Price Information
    for t_pair in structured_pairs:
        task1 = get_quote(t_pair['combined'])
        print(task1)
          

step_2()
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
step_2()

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