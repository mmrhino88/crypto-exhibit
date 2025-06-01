"""
Created on Wed Apr 6 17:24:18 2025

@author: ymm
"""
import time
import json
import asyncio
from data.base_data import BaseStreamData


class KucoinStreamPriceData(BaseStreamData):
    """
    Streaming data class for Kucoin symbol price data.
    This has best bid and ask and size
    """
    def __init__(self, params):
        # Resolve params
        super().__init__(params)

        self.topics = params.get('topics', ["/market/ticker"])
        self.private = params.get('private', False)
        self.symbols = params.get('symbols')
        self.symbols = [self.symbols] if isinstance(self.symbols, str) else self.symbols
        
        # Authenticate
        self.authenticate()

    def stream(self, callback):
        """
        Start streaming
        """
        async def wrapper():
            await self._connect(callback)

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(wrapper())
        else:
            loop.run_until_complete(wrapper())

    async def subscribe(self, topics=None):
        """
        Subscribe to all symbols to stream
        """
        for sym in self.symbols:
            topic = f"/market/ticker:{sym}"
            sub_msg = {
                "id": str(int(time.time() * 1000)),
                "type": "subscribe",
                "topic": topic,
                "response": True
            }
            await self.ws.send(json.dumps(sub_msg))
            print(f"Subscribed to {topic}")


class KucoinStreamAccountData(BaseStreamData):
    """
    Streaming data class for account and order updates
    """
    def __init__(self, params):

        # Resolve params
        super().__init__()
         
        self.topics = params.get('topics', ["/spotMarket/tradeOrdersV2"])
        self.private = params.get('private', True)
        
        # Authenticate for private streams
        self.authenticate()

    def stream(self, callback):
        """
        Start streaming with custom msg handler callback func
        """
        async def wrapper():
            await self._connect(callback)

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(wrapper())
        else:
            loop.run_until_complete(wrapper())

    async def subscribe(self, topics=["/spotMarket/tradeOrdersV2"]):
        """
        Subscribe to account update topics
        """
        for topic in topics:
            sub_msg = {
                "id": str(int(time.time() * 1000)),
                "type": "subscribe",
                "topic": topic,
                "privateChannel": True,
                "response": True
            }
            await self.ws.send(json.dumps(sub_msg))
            print(f"Subscribed to private topic: {topic}")

    async def submit_market_order(self, symbol, side, size):
        """
        Market orders
        """
        try:
            order = await self.client.create_market_order(symbol, side=side, size=size)
            order_id = order['orderId']
            print(f"Submitted/Finished {side.upper()} order {symbol}, size {size}, orderId {order_id}")
            return order_id
        except Exception as e:
            print(f"Failed to submit {side} order for {symbol}: {e}")
            return None

    async def submit_test_market_order(self, symbol, side, size):
        """
        Test market orders
        """
        try:
            order = await self.client.create_test_order(symbol, type='market', side=side, size=size)
            order_id = order['orderId']
            print(f"Submitted {side.upper()} order {symbol}, size {size}, orderId {order_id}")
            return order_id
        except Exception as e:
            print(f"Failed to submit {side} order for {symbol}: {e}")
            return None
