# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 13:25:26 2019

@author: tinog
"""

import numpy as np
from math import log
from typing import Iterable

def signed_log(data, base="Ten"):
    """
    Returns a signed logarithm of data
    
    Args:
        data (numeric / list / array / series): data to be transformed
        base (string / numeric): base of logarithm, can be number or a string 
                                 with these values: Two, Zero, Ten, Natural
        
    Returns:
        signed logarithm of data
    """
    
    absolut = np.abs(data)
    signed = np.sign(data)
    
    if base == "Two":
        return signed * np.log2(absolut + 1)
    if base == "Zero":
        return signed * np.log1p(absolut)
    if base == "Ten":
        return signed * np.log10(absolut + 1)
    if base == "Natural":
        return signed * np.log(absolut)
    
    try:
        if isinstance(absolut, Iterable) == False:
            absolut = np.array(absolut)
        loged_data = []
        for item in absolut:
            loged_data.append(log(item, float(base)) * log(float(base)))
        return signed * loged_data
    except:
        return signed * np.log10(absolut)