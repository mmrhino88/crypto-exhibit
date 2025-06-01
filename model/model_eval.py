"""
Created on Wed Apr 23 17:46:08 2025

@author: ymm
"""
import importlib

class ModelEvalEngine(object):
    
    def __init__(self, params):
        
        self.model_type = params.get('model_type', 'TS')
        self.model = params.get('model', None)
    
    def load_data(self, start, end):
        """
        Load data as specified by model's data map
        """
        data_map = self.model.load_data_map()
        
        data = {}
        for input_name, content in data_map.items():
            
            # Load data class module
            module = content['module']
            module = importlib.import_module(module)
            data_cls = getattr(module, input_name)
            
            # Instantiate data class
            params = content['params']
            data_loader = data_cls(params)
            
            # Load data
            data[input_name] = data_loader.load(start, end)
        
        return data
    
    
    def run(self, start, end, data=None):
        """
        Run model eval
        
        Steps
            - Load data based on model's specified data map
            - Run model eval, generate raw signals
            - TODO: normalize signals
        """      
        # Get data
        if not data:
            data = self.load_data(start=start, end=end)
        
        # Eval signal (raw scores)
        if self.model_type == 'TS':
            results = self.model.ts_eval(start, end, data)
        else:
            results = self.model.cs_eval(start, end, data)
            
        # Normalize signals
        pass
        
        return results
  