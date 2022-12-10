from alpaca_trade_api import  REST
import requests
from functions import HEADERS, rest_api, API_KEY, API_SECRET_KEY
import json
import pandas as pd
from functions import post_Alpaca_order, min_arb_percent, rest_api
import asyncio


DATA_URL = 'https://data.alpaca.markets'
endpoint = "https://paper-api.alpaca.markets/v2/assets"

def get_coin_tickers():
    req=requests.get(endpoint, headers=HEADERS)
    json_resp = json.loads(req.text)
    print(json_resp)
    return json_resp


def collect_tradeables(json_obj):
    # create empty list to store tradeable pairs
    tradeable_pairs = []

    # iterate over each asset in json_obj
    for asset in json_obj:
        # check if asset is a cryptocurrency and not frozen or post-only
        if asset["class"] == "crypto" and asset["status"] == "active":
            # append ticker to tradeable_pairs list
            tradeable_pairs.append(asset["symbol"])

    # return list of tradeable pairs
    return tradeable_pairs


    # Structure Arbitrage Pairs
def structure_triangular_pairs(coin_list):

    # Declare Variables
    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = coin_list[0:]

    # Get Pair A
    for pair_a in pairs_list:
        pair_a_split = pair_a.split("/")
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]

        # Assign A to a Box
        a_pair_box = [a_base, a_quote]

        # Get Pair B
        for pair_b in pairs_list:
            pair_b_split = pair_b.split("/")
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]

            # Check Pair B
            if pair_b != pair_a:
                if b_base in a_pair_box or b_quote in a_pair_box:

                    # Get Pair C
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split("/")
                        c_base = pair_c_split[0]
                        c_quote = pair_c_split[1]

                        # Count the number of matching C items
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            counts_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    counts_c_base += 1

                            counts_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    counts_c_quote += 1

                            # Determining Triangular Match
                            if counts_c_base == 2 and counts_c_quote == 2 and c_base != c_quote:
                                combined = pair_a + "," + pair_b + "," + pair_c
                                unique_item = ''.join(sorted(combine_all))

                                if unique_item not in remove_duplicates_list:
                                    match_dict = {
                                        "a_base": a_base,
                                        "b_base": b_base,
                                        "c_base": c_base,
                                        "a_quote": a_quote,
                                        "b_quote": b_quote,
                                        "c_quote": c_quote,
                                        "pair_a": pair_a,
                                        "pair_b": pair_b,
                                        "pair_c": pair_c,
                                        "combined": combined
                                    }
                                    triangular_pairs_list.append(match_dict)
                                    remove_duplicates_list.append(unique_item)
    return triangular_pairs_list


def get_quote(symbol: str, prices):
    '''
    Get quote data from Alpaca API
    '''
 
    try:
        # make the request
            quote = requests.get('{0}/v1beta2/crypto/latest/trades?symbols={1}'.format(DATA_URL, symbol), headers=HEADERS)
            prices[symbol] = quote.json()['trades'][symbol]['p']
            # Status code 200 means the request was successful
            if quote.status_code != 200:
                print("Undesirable response from Alpaca! {}".format(quote.json()))
                return False
            else: 
                return prices
 
    except Exception as e:
        print("There was an issue getting trade quote from Alpaca: {0}".format(e))
        return False

async def get_price_for_t_pair(t_pair):

    # Extract Pair Info
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    prices = {
    pair_a : 1,
    pair_b : 1,
    pair_c : 1
    }
    # Extract Price Information for Given Pairs
    pair_a_p = get_quote(pair_a, prices)
    pair_b_p = get_quote(pair_b, prices)

    pair_c_p = get_quote(pair_c, prices)
   
    # Output Dictionary
    return pair_c_p, t_pair


def check_arbitrage(prices, min_arb):
    # Extract the relevant pairs from the prices dictionary
    df=[]
    #ticker=[]
    for i in prices: 
        df.append(prices[i])
        #ticker.append(i)


   # Calculate the profit from triangular arbitrage
    profit = (df[0] * df[2]) / df[1] - 1
    print(profit)

    # Check if the profit is higher than 0.3%
    if profit > min_arb:
        strategy= "forward"
        print("there is an arbitrage opportunity, positive" )
    elif profit < -min_arb:
        strategy= "reverse"
        print("there is an arbitrage opportunity, negative" )
        return True
    else:
        strategy=None
        return False

"""def execute_trades(trades, initial_budget,base_quotes ):
    df=[]
    tickers=[]
    # Loop through the list of trades
    for i in trades:
        # Get the current price for each currency pair
        df.append(trades[i])
        tickers.append(i)
    print(tickers)


    PAIR1 = df[0]
    print(F'Pair1',PAIR1)
    PAIR3 = df[2]

    PAIR2 = df[1]
    DIV = PAIR1 / PAIR3
    spread = abs(DIV - PAIR2)
    QUANTITY1= initial_budget/PAIR1
    QUANTITY21=QUANTITY1/PAIR2
    QUANTITY22=QUANTITY1*PAIR2
    




    order1= post_Alpaca_order(tickers[0], QUANTITY1, "buy")
    print(f'quantity1', QUANTITY1)

    if order1.status_code == 200:
        if base_quotes['a_base']== base_quotes['b_quote']:
                
            order2 = post_Alpaca_order(tickers[1], QUANTITY21, "buy")
            print(f'order_buy', order2.content)
            print(f'quantities21', QUANTITY21)
            if order2.status_code == 200:
                QUANTITY3=QUANTITY21*PAIR3
                print(f'strategy 1',QUANTITY3)
                order3 = post_Alpaca_order(tickers[2], QUANTITY3, "sell")
        elif base_quotes['a_base'] ==base_quotes['b_base']:
            order2 = post_Alpaca_order(tickers[1], QUANTITY22, "sell")
            print(f'order2', order2.content)
            if order2.status_code == 200:
                QUANTITY3=QUANTITY21*PAIR3
                print(f'strategy 1',QUANTITY3)
                order3 = post_Alpaca_order(tickers[2], QUANTITY3, "sell")

            else:
                #post_Alpaca_order(tickers[0], QUANTITY1, "sell")
                print("Bad Order 3")
                exit()   

        else:
            post_Alpaca_order(tickers[0], QUANTITY1, "sell")
            print("Bad Order 2")
            exit()   
    else:
        print("Bad Order 1")
        exit()   """

# Calculate Surface Rate Arbitrage Opportunity
def calc_triangular_arb_surface_rate(t_pair, prices, starting_amount):

    # Set Variables
    starting_amount = starting_amount
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0

    # Extract Pair Variables
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    df=[]
    tickers=[]
    # Loop through the list of trades
    for i in prices:
        # Get the current price for each currency pair
        df.append(prices[i])
        tickers.append(i)
    

    # Extract Price Information
    a_p = df[0]
    b_p = df[1]
    c_p = df[2]

    #direction=strategy
    # Set directions and loop through
    direction_list = ["forward", "reverse"]
    for direction in direction_list:

        # Set additional variables for swap information
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0
        """
            Poloniex Rules !!
            If we are swapping the coin on the left (Base) to the right (Quote) then * (1 / Ask)
            If we are swapping the coin on the right (Quote) to the left (Base) then * Bid
        """

        # Assume starting with a_base and swapping for a_quote
        if direction == "forward":
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = 1 / a_p
            direction_trade_1 = "base_to_quote"

        # Assume starting with a_base and swapping for a_quote
        if direction == "reverse":
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_p
            direction_trade_1 = "quote_to_base"

        # Place first trade
        contract_1 = pair_a
        acquired_coin_t1 = starting_amount #* swap_1_rate

        """  FORWARD """
        # SCENARIO 1 Check if a_quote (acquired_coin) matches b_quote
        if direction == "forward":
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = b_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1
                print("scenario1")

        # SCENARIO 2 Check if a_quote (acquired_coin) matches b_base
        if direction == "forward":
            if a_quote == b_base and calculated == 0:
                swap_2_rate = 1 / b_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c
                print("scenario2")

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 3 Check if a_quote (acquired_coin) matches c_quote
        if direction == "forward":
            print("scenario3")
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = c_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c
            


                # not intuitive c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1
                    print("Not intuitive STRATEGY")
                    order1 = post_Alpaca_order(tickers[0], acquired_coin_t2, "buy")
                    if order1.status_code == 200:
                        
                        order2 = post_Alpaca_order(tickers[1], acquired_coin_t2, "sell")
                   
                        if order2.status_code == 200:
                            order3 = post_Alpaca_order(tickers[2], acquired_coin_t3, "sell")

                            if order3.status_code == 200:
                                print(f'Done', tickers)
                                
                                
                            else:
                                post_Alpaca_order(tickers[1], acquired_coin_t2, "buy")
                                print("Bad Order 3")
                                print(order3.content)
                                exit()
                        else:
                            post_Alpaca_order(tickers[0], acquired_coin_t2, "sell")
                            print("Bad Order 2")
                            print(order2.content)
                            exit()
                    else:
                        print("Bad Order 1")
                        exit()
                #NORMAL If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b
                    acquired_coin_t2 = acquired_coin_t1 / swap_2_rate
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1
                    
                    print("NORMAL STRATEGY")
                    order1 = post_Alpaca_order(tickers[0], acquired_coin_t2, "buy")
                    if order1.status_code == 200:
                        print(order1.content)
                        order2 = post_Alpaca_order(tickers[1], acquired_coin_t3, "buy")
                        print(order2.content)
                        if order2.status_code == 200:
                            
                            order3 = post_Alpaca_order(tickers[2], acquired_coin_t3, "sell")
                           
                            if order3.status_code == 200:
                                print(f'Done', tickers)                                
                            else:
                                post_Alpaca_order(tickers[1], acquired_coin_t3, "sell")
                                print("Bad Order 3")
                                print(order3.content)
                                exit()
                        else:
                            post_Alpaca_order(tickers[1], acquired_coin_t2, "sell")
                            print("Bad Order 2")
                            print(order2.content)
                            exit()
                    else:
                        print("Bad Order 1")
                        print(order1.content)
                        exit()
                                
            

                
        # SCENARIO 4 Check if a_quote (acquired_coin) matches c_base
        if direction == "forward":
            if a_quote == c_base and calculated == 0:
                swap_2_rate = 1 / c_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                print("scenario4")
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        
        """  REVERSE """
        # SCENARIO 1 Check if a_base (acquired_coin) matches b_quote
        if direction == "reverse":
            if a_base == b_quote and calculated == 0:
                swap_2_rate = b_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b
                
                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1
                print("scenario1 - Reverse")
        # SCENARIO 2 Check if a_base (acquired_coin) matches b_base
        if direction == "reverse":
            if a_base == b_base and calculated == 0:
                swap_2_rate = 1 / b_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1
                print("scenario2 - Reverse")
        # SCENARIO 3 Check if a_base (acquired_coin) matches c_quote
        if direction == "reverse":
            if a_base == c_quote and calculated == 0:
                swap_2_rate = c_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1
                print("scenario3 - Reverse")
        # SCENARIO 4 Check if a_base (acquired_coin) matches c_base
        if direction == "reverse":
            if a_base == c_base and calculated == 0:
                swap_2_rate = 1 / c_p
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_p
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_p
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                print("scenario4 - Reverse")
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        """ PROFIT LOSS OUTPUT """

        # Profit and Loss Calculations
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0



base_quotes={'a_base': 'SOL', 'b_base': 'SOL', 'c_base': 'USDT', 'a_quote': 'USD', 'b_quote': 'USDT', 'c_quote': 'USD', 'pair_a': 'SOL/USD', 'pair_b': 'SOL/USDT', 'pair_c': 'USDT/USD', 'combined': 'SOL/USD,SOL/USDT,USDT/USD'}
#{'a_base': 'USDT', 'b_base': 'AAVE', 'c_base': 'AAVE', 'a_quote': 'USD', 'b_quote': 'USDT', 'c_quote': 'USD', 'pair_a': 'USDT/USD', 'pair_b': 'AAVE/USDT', 'pair_c': 'AAVE/USD', 'combined': 'USDT/USD,AAVE/USDT,AAVE/USD'}


prices={'SOL/USD': 13.5848, 'SOL/USDT': 13.578, 'USDT/USD': 1}
#{'USDT/USD': 1, 'AAVE/USDT': 61.72, 'AAVE/USD': 61.71}

initial_budget= 100
#execute_trades(prices, initial_budget, base_quotes)
"""calc_triangular_arb_surface_rate(base_quotes, prices)"""