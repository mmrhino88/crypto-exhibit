#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 17:24:18 2025

@author: ymm
"""

from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
import settings
import pandas as pd

# Websocket data imports
import asyncio
import time
import json
import websockets

# Kucoin
from kucoin.client import Client
from kucoin.async_client import AsyncClient

# Time frequency map
FREQ_MAP = {
    '1day':     pd.Timedelta(days=1),
    '1week':    pd.Timedelta(days=7),
    '1s':       pd.Timedelta(seconds=1),
    '1min':     pd.Timedelta(minutes=1),
    '5min':     pd.Timedelta(minutes=5),
    '15min':    pd.Timedelta(minutes=15),
    '30min':    pd.Timedelta(minutes=30),
    '60min':    pd.Timedelta(minutes=60)
}


class BaseData(ABC):
    """
    Abstract base class for all data classes
    """

    def __init__(self, params=None):
        if params is None:
            params = {}
            
        self.start = params.get('start', None)
        self.end = params.get('end', None)
        self.client = None
        
        self.authenticate()

    def authenticate(self):
        """Instantiate client and authenticate"""
        # Load dotenv
        load_dotenv(dotenv_path=os.path.join(settings.PROJECT_ROOT, "keys.env"))

        api_key = os.getenv("KUCOIN_API_KEY")
        api_secret = os.getenv("KUCOIN_API_SECRET")
        api_passphrase = os.getenv("KUCOIN_API_PASSPHRASE")
        base_url = "https://api.kucoin.com"
        
        self.client = Client(api_key, api_secret, api_passphrase)

    @abstractmethod
    def load(self, *args, **kwargs):
        """Load data"""
        pass
    
    @abstractmethod
    def loc(self, *args, **kwargs):
        """Locate data"""
        pass
    
    
class BaseStreamData(ABC):
    """
    Abstract base class for Kucoin streaming data providers
    """
    def __init__(self, params=None):
        if params is None:
            params = {}
            
        # Common streaming state
        self.token = None
        self.ws = None
        self._connected = False
        self._running = True
        self.queue = asyncio.Queue()
        self.client = None

    def authenticate(self):
        """
        Instantiate client and authenticate
        """
        # Load environment variables for private streams
        load_dotenv(dotenv_path=os.path.join(settings.PROJECT_ROOT, "keys.env"))
        
        api_key = os.getenv("KUCOIN_API_KEY")
        api_secret = os.getenv("KUCOIN_API_SECRET")
        api_passphrase = os.getenv("KUCOIN_API_PASSPHRASE")
        
        self.client = AsyncClient(api_key, api_secret, api_passphrase)

    async def _ping(self):
        """
        Send periodic pings to keep the connection alive
        """
        while self._connected and self.ws:
            try:
                ping_msg = {"id": str(int(time.time() * 1000)), "type": "ping"}
                await self.ws.send(json.dumps(ping_msg))
            except Exception as e:
                print("Ping error:", e)
            await asyncio.sleep(20)

    async def _queue_loop(self):
        """
        Queue incoming messages
        """
        while self._running:
            try:
                msg = await self.ws.recv()
                await self.queue.put(msg)
            except Exception as e:
                print("Error receiving message:", e)
                self.stop()
                break

    async def _get_ws_endpoint(self):
        """
        This is to get token for ws connection
        """
        resp = await self.client.get_ws_endpoint(private=self.private)
        endpoint = resp['instanceServers'][0]['endpoint']
        self.token = resp['token']
        return f"{endpoint}?token={self.token}"

    async def _connect(self, callback, sleep=0.05):
        """
        Base connection structure to WebSocket and handle messages
        """
        ws_url = await self._get_ws_endpoint()
        
        try:
            async with websockets.connect(ws_url, ping_interval=None) as ws:
                self.ws = ws
                self._connected = True

                # Launch background receive loop
                asyncio.create_task(self._queue_loop())
            
                # Start ping task
                asyncio.create_task(self._ping())
                
                # Subscribe to topics
                await self.subscribe()

                # Process messages
                while self._running:
                    try:
                        msg = await self.queue.get()
                        parsed = json.loads(msg)
                        await callback(parsed)
                    except Exception as e:
                        print("Error processing message:", e)
                        self.stop()
                        break
                    
                    if sleep > 0:
                        await asyncio.sleep(sleep)
                    
                    if not self._running:
                        await self.ws.close()
                        break

        except Exception as e:
            print(f"Error in connecting to WebSocket: {e}")
            # TODO: attempt to reconnect
    
    def stop(self):
        """Stop the stream"""
        self._running = False
        self._connected = False
        
    @abstractmethod
    def stream(self, callback):
        """High level stream method with message handler callback"""
        pass

    @abstractmethod
    async def subscribe(self, topics=None):
        """Custom subscriber for child classes"""
        pass
