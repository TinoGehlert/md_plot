# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 10:59:45 2019

@author: tinog_000
"""

import pandas as pd
from pandas.api.types import is_numeric_dtype
from scipy.stats.mstats import mquantiles
from math import ceil

def optimal_no_bins(data):
    """
    Estimation of optimal number of bins for using in histogram
    (Keating/Scott 99)
    
    Args:
        data (pandas series): one dimensional data vector
    
    Returns:
        optimal number of bins for a histogram
    """
    if not isinstance(data, pd.Series):
        try:
            data = pd.Series(data)
        except:
            raise Exception("Data cannot be converted into pandas series")
    if not is_numeric_dtype(data):
        raise Exception("Data is not numeric!")
    
    data = data.dropna()
    nData = len(data)
    if nData == 0:
        return 0
    
    sigma = data.std()
    p = mquantiles(data, [0.25, 0.75], alphap=1/3, betap=1/3)
    interquartilRange = p[1] - p[0]
    sigmaSir = min(sigma, interquartilRange / 1.349)
    optBinWidth = (3.49 * sigmaSir) / (nData**(1/3))
    
    if optBinWidth > 0:
        optNrOfBins = max(ceil((data.max() - data.min()) / optBinWidth), 10)
    else:
        optNrOfBins = 10
    
    return optNrOfBins