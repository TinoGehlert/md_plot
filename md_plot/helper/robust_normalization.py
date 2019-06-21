# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 11:52:19 2019

@author: tinog
"""

import warnings
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

def robust_normalization(data, centered=False, capped=False, narm=True, 
                         withBackTransformation=False):
    """
    This function normalizes all numeric columns of a pandas dataframe or a 
    single pandas series
    
    Args:
        data (dataframe / series): data to be normalized
        centered (boolean): centeres normalized data to center = 0
        capped (boolean): cuts values below and above the normalization limits
        narm (boolean): removes infinite values
        withBackTransformation (boolean): provides information to denormalize 
                                          the data again
    
    Return:
        Normalized data as dataframe or a dictionary containing the normalized 
        data as dataframe and all information to denormalize the data
    """
    
    # replace infinte vales by nan
    if narm == True:
        data = data.replace([np.inf, -np.inf], np.nan)
    
    #__________________________________________________________NORMALIZE SERIES
    center=0
    if isinstance(data, pd.Series):
        minX = data.quantile(0.01)
        maxX = data.quantile(0.99)
        denom = maxX - minX
        if denom == 0:
            denom = 1
        data = (data - minX) / denom
        
        if centered == True:
            center = data.median()
            data = data - center
            if capped == True:
                data = data.apply(lambda x: -1 if x < -1 else x)
                data = data.apply(lambda x: 1 if x > 1 else x)
        else:
            if capped == True:
                minX = data.quantile(0.01)
                maxX = data.quantile(0.99)
                data = data.apply(lambda x: minX if x < minX else x)
                data = data.apply(lambda x: maxX if x > maxX else x)
        
        if withBackTransformation == True:
            return {"TransformedData": data, "MinX": minX, "MaxX": maxX, 
                    "Denom": denom, "Center": center}
        else:
            return data
    
    #_______________________________________________________NORMALIZE DATAFRAME
    if isinstance(data, pd.DataFrame):
        if withBackTransformation == True:
            lstCols = list(data.columns)
            dataOut = pd.DataFrame()
            minX = {}
            maxX = {}
            denom = {}
            center = {}
            for strCol in lstCols:
                if is_numeric_dtype(data[strCol]):
                    xtrans = robust_normalization(data[strCol], 
                                                  centered=centered, 
                                                  capped=capped, 
                                                  narm=narm, 
                                withBackTransformation=withBackTransformation)
                    dataOut[strCol] = xtrans["TransformedData"]
                    minX[strCol] = xtrans["MinX"]
                    maxX[strCol] = xtrans["MaxX"]
                    denom[strCol] = xtrans["Denom"]
                    center[strCol] = xtrans["Center"]
            return {"TransformedData": dataOut, "MinX": minX, "MaxX": maxX, 
                    "Denom": denom, "Center": center}
        else:
            lstCols = list(data.columns)
            dataOut = pd.DataFrame()
            for strCol in lstCols:
                if is_numeric_dtype(data[strCol]):
                    xtrans = robust_normalization(data[strCol], 
                                                  centered=centered, 
                                                  capped=capped, 
                                                  narm=narm, 
                                withBackTransformation=withBackTransformation)
                    dataOut[strCol] = xtrans
            return dataOut
    
    #____________________________________________________HANDLE WRONG DATA TYPE
    warnings.warn("Data is not a pandas dataframe or series, try to convert "\
                  "it to a dataframe")
    try:
        return robust_normalization(pd.DataFrame(data), centered, capped, narm)
    except:
        raise Exception("It did not work")