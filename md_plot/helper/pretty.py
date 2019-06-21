# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 15:10:49 2019

@author: tinog
"""

import numpy as np

# basic implementation based on:
# https://stackoverflow.com/questions/43075617/python-function-equivalent-to-rs-pretty
# Bias feature based on R's pretty function:
# https://svn.r-project.org/R/trunk/src/appl/pretty.c
def nice_step(x, h=None, h5=None):
    # calculates step size
    
    if h is None:
        h = 1.5
    if h5 is None:
        h5 = 0.5 + 1.5*h
    
    exp = np.floor(np.log10(x))
    f   = x / 10**exp
    
    if f <= (2+h)/(1+h):
        nf = 1.
    if (f > (2+h)/(1+h)) & (f <= (5+2*h5)/(1+h5)):
        nf = 2.
    if (f > (5+2*h5)/(1+h5)) & (f <= (10+5*h)/(1+h)):
        nf = 5.
    if f > (10+5*h)/(1+h):
        nf = 10.

    return nf * 10.**exp


def pretty(low, high, n, h=None, h5=None):
    """
    Compute a sequence of about n+1 equally spaced ‘round’ values which cover 
    the range of the values in x. The values are chosen so that they are 
    1, 2 or 5 times a power of 10.
    
    Args:
        low (numeric): lower bound of range
        high (numeric): upper bound of range
        n (int): number of breakpoints
        h (float): non-negative numeric, typically > 1. The interval unit is 
                   determined as {1,2,5,10} times b, a power of 10. Larger h 
                   values favor larger units.
        h5 (float): non-negative numeric multiplier favoring factor 5 over 2. 
                    Default and ‘optimal’: h5 = 0.5 + 1.5*h
    
    Returns:
        Numpy array of new interval breakpoints
    """
    if h is None:
        h = 1.5
    if h5 is None:
        h5 = 0.5 + 1.5*h
    
    d     = nice_step((high - low) / n, h, h5)
    miny  = np.floor(low  / d) * d
    maxy  = np.ceil (high / d) * d
    return np.arange(miny, maxy+0.5*d, d)