#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 29 19:10:21 2025

@author: ymm

Test script to run model eval
"""
from datetime import datetime

from model.model_eval import ModelEvalEngine
from data.kucoin_futures_data import KucoinFuturesSymbolData
from model.momentum import Momentum

#%% Set up

# Define universe
universe_data = KucoinFuturesSymbolData()
universe = universe_data.load()
universe = universe_data.filter_symbols(universe, top=3)
symbols = universe.symbol.unique().tolist()

# Define time period
start = datetime(2025, 3, 1)
end = datetime(2025, 4, 1)

min_interval = 60
lookback_periods = 20

# Set up model
model_params = {
    'type': 'futures',
    'symbols': symbols,
    'freq': min_interval, 
    'lookback': lookback_periods, 
}
model = Momentum(model_params)

#%% Run model eval

eval_params = {"model": model}
mee = ModelEvalEngine(eval_params)
raw_signals = mee.run(start, end)
    
print("====Raw signals====\n\n", raw_signals.head())
