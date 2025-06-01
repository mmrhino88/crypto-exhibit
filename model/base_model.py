#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 17:31:46 2025

@author: ymm
"""
from abc import ABC, abstractmethod, abstractproperty


class Model(ABC):
    """Base model class"""
    
    def __init__(self, params):
        
        self._params = params
        
    # def __repr__(self, *args, **kwargs):
    #     """A string representation of a model"""
    #     return "{}Model({})".format(type(self).__name__, self.param_str)
    
    @abstractmethod
    def load_data_map(self):
        """Returns what data is required for this model, in a dict"""
        pass
    
    @abstractmethod
    def cs_eval(self, date, data):
        """Evaludate model on a point in time date"""
        pass
    
    @abstractmethod
    def ts_eval(self, start_date, end_date, data):
        """Evaludate model on a time series"""
        pass
        
    @abstractproperty
    def param_str(self):
        return 'This is base param_str'
    
        
    
