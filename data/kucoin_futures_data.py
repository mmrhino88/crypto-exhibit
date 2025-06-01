#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 4 20:08:56 2025

@author: ymm
"""
from datetime import datetime
import pandas as pd
import numpy as np
from data.base_data import BaseData, FREQ_MAP


class KucoinFuturesSymbolData(BaseData):
    """
    Get all symbols from Kucoin
    NOTE: This is not PIT!
    """
    
    def __init__(self):
        super().__init__({})
        self.authenticate()

    def load(self, quote=['USDT']):
        """Load all tickers from Kucoin"""
        
        # Get all tickers
        data = self.client.futures_get_symbols()
        data = pd.DataFrame(data)
        data = data.apply(pd.to_numeric, errors='ignore')
        
        # Filter quote currency
        data = data[data['quoteCurrency'].isin(quote)]

        print("Loaded Kucoin futures symbol universe")
        return data

    def loc(self, start, end):
        """Locate data (not implemented for non time dependent data)"""
        pass
    
    def filter_symbols(self, 
                       data, 
                       top=None, 
                       threshold=None, 
                       by='volValue',
                       min_dollar_vol=None,
                       min_booksize=None):
        """Filter by top liquidity or by volume percentile threshold,
        if both provided, prioritize top"""
        
        # Compute dollar volume
        data['dollarVol24h'] = data['markPrice'] * data['volumeOf24h']
        data = data.sort_values('dollarVol24h', ascending=False)
        
        # Filter minimum volume
        if min_dollar_vol is not None:
            data = data[data['dollarVol24h'] >= min_dollar_vol]
        
        if min_booksize is not None:
            pass  # TODO: Implement this
        
        # Filter securities by rank or threshold
        if top is not None:
            data_filtered = data.iloc[:top].copy()
        elif threshold is not None:
            val = data['dollarVol24h'].quantile(threshold)
            data_filtered = data[data[by] >= val].copy()
            
        return data_filtered


class KucoinFuturesKlinesData(BaseData):

    def __init__(self, params):
        # Resolve params
        super().__init__(params)

        self.symbols = params['symbols']
        self.freq = params.get('freq', '1day')
        self.lookback = params.get('lookback', 0)
        self.offset = params.get('offset', 0)
        
        # Initialize client
        self.authenticate()        

    def batch_load(self, 
                   sym: str, 
                   freq: int, 
                   start: datetime, 
                   end: datetime, 
                   batch_size: int=200):
        """Load klines in batches"""
        
        # Get datetime interval list
        freq_ms  = freq * 60 * 1000
        batch_ms = freq_ms * batch_size
        N_batches = int(np.ceil((end - start + freq_ms) / batch_ms))
        
        print(f"Loading {sym} kline data in {N_batches} batches...")
            
        df = []
        for batch_i in range(N_batches):
            
            start_ = start + batch_ms * batch_i
            end_   = start + batch_ms * (batch_i + 1)
            end_   = min(end_, end)
            
            # Get batch data
            klines = self.client.futures_get_klines(sym, 
                                                    kline_type=self.freq, 
                                                    start=start_, 
                                                    end=end_)

            # Format into pandas df
            df_ = pd.DataFrame(klines, columns=[
                "timestamp",
                "open", 
                "close", 
                "high", 
                "low", 
                "volume"
            ])
    
            df_["timestamp"] = pd.to_datetime(df_["timestamp"].astype(int), unit="ms")
            df_ = df_.astype({
                "open":     float,
                "close":    float,
                "high":     float,
                "low":      float,
                "volume":   float,
            })
            
            df.append(df_)
            
        df = pd.concat(df, axis=0)
        df['symbol'] = sym
        df = df.sort_values("timestamp").reset_index(drop=True)
        
        return df
        
    def load(self, start: datetime=None, end: datetime=None):
        """Load all klines data"""
        
        # Resolve symbols
        if not isinstance(self.symbols, list):
            self.symbols = [self.symbols]
            
        # Resolve start and end times
        lookback = self.lookback * self.freq * pd.Timedelta(minutes=1)
        start = start - lookback
        
        if not isinstance(start, int):
            start = int(start.timestamp() * 1000)
        if not isinstance(end, int):
            end = int(end.timestamp() * 1000)

        # Get data for each symbol
        data = {}
        for sym in self.symbols:
            
            df = self.batch_load(sym, self.freq, start, end)
            
            print('Obtained futures klines data for {} over {} - {}'.format(sym, start, end))
            data[sym] = df
            
        return data 
    
    def loc(self, start, end):
        """To be implemented for cross-sectional eval"""
        pass