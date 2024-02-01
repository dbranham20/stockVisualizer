"""Quotes Publisher

Purpose: this quotes publisher servers as server for live stock data. For
this project, it generates random data for stock prices and publishes them.

Each second, it publishes a dictionary with keys as stock tickers, and values
as the last 5 quotes in the past 5 seconds.

NOTE:
The starter code for this module was taken from the example provided in
dash_extensions page: https://www.dash-extensions.com/components/event_source
however, it is slightly modified for the purpose of this project
"""

import asyncio
import json
import random
import uvicorn
from sse_starlette import EventSourceResponse
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


middleware = Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"]
)
server = Starlette(middleware=[middleware])


_STOCK_QUOTES = {
    "STK1": [137.76, 138, 138.5, 138.25, 137.5],
    "STK2": [92.86, 92.5, 92, 91, 91.5],
    "STK3": [135.69, 136, 136.5, 135.75, 136],
    "STK4": [250.17, 250.5, 251, 250, 251],
    "STK5": [129.20, 130, 129.5, 130, 130.5],
    "TIMESTAMP": [-1, -2, -3, -4, -5]
}


async def random_stock_data():
    """This the main generator for live data, see module __docstring__ for
    details"""
    global _STOCK_QUOTES
    while True:
        await asyncio.sleep(1)
        for (stock, values) in _STOCK_QUOTES.items():
            if stock != "TIMESTAMP":
                values.append(
                    (1 + random.randrange(-10, 10) / 100) * values[-1]
                )
                del values[0]
        json.dumps(_STOCK_QUOTES)
        yield json.dumps(_STOCK_QUOTES)


@server.route("/stocks_data")
async def sse(request):
    """This route is used for subscribers who wish to subscribe for live data
    published by the publishers"""
    generator = random_stock_data()
    return EventSourceResponse(generator)

if __name__ == "__main__":
    uvicorn.run(server, port=5000)
