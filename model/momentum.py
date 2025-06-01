#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 21:28:47 2025

@author: ymm
"""
from model.base_model import Model
import numpy as np
import pandas as pd


class Momentum(Model):
    """Toy momentum model"""
    
    def __init__(self, params):
        self.symbols = params['symbols']
        self.freq = params['freq']
        self.lookback = params['lookback']
        
    def load_data_map(self):
        """
        Load data map for this model. Data maps describes the set
        of data needed to evaluate this model. 
        
        TODO: Add registration step in eval engine, and 
              decouple module path from this
        """
        data_map = {
            'KucoinFuturesKlinesData': {
                'module': 'data.kucoin_futures_data',
                'params': {
                    'symbols': self.symbols,
                    'freq': self.freq,
                    'lookback': self.lookback,
                    }
                }
            }
        
        return data_map
        
    def cs_eval(self, date, data):
        """Evaludate model on a point in time date"""
        pass

    def ts_eval(self, start, end, data):
        """Evaludate model on a time series"""
        
        # Locate data
        klines = data['KucoinFuturesKlinesData']
        df = pd.concat(list(klines.values()), axis=0)
        
        eval_dt = df['timestamp']
        eval_dt = eval_dt[(eval_dt >= start) & (eval_dt <= end)].copy()
        
        # Pivot to T X N matrix
        df_pivot = df.pivot_table(index='timestamp', values='close', columns='symbol')
        
        # Use log return
        df_pivot = df_pivot.apply(lambda x: np.log(x / x.shift(1)))
        
        # Calculate rolling momentum
        df_out = df_pivot.rolling(window=self.lookback, min_periods=self.lookback).sum()
        
        return df_out
 