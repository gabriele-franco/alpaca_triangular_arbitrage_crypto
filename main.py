import alpaca_trade_api as tradeapi
from alpaca_trade_api import StreamConn, REST
import requests
import asyncio
from functions import get_quote, check_arb, waitTime, rest_api, get_account_data

import streamlit as st



async def main():
        while True:
            task1 = loop.create_task(get_quote("ETH/USD"))
            task2 = loop.create_task(get_quote("BTC/USD"))
            task3 = loop.create_task(get_quote("ETH/BTC"))
            # Wait for the tasks to finish
            await asyncio.wait([task1, task2, task3])
            await check_arb()
            cash= get_account_data()
            st.write("Soldi Liquidi",cash)
            #st.write("equity",equity)
            # # Wait for the value of waitTime between each quote request
            await asyncio.sleep(waitTime)



loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
