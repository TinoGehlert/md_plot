# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 11:31:37 2019

@author: tinog
"""

import warnings
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
from .pareto_radius import pareto_radius
from .optimal_no_bins import optimal_no_bins
from .pretty import pretty

def pareto_density_estimation(data, paretoRadius=None, kernels=None, 
                              minAnzKernels=100):
    """
    Estimates the Pareto Density for a one dimensional distibution
    this is the best density estimation to judge Gaussian Mixtures of the Data
    see [Ultsch 2003]
    
    Args:
        data (pandas series): one dimensional data vector
        paretoRadius (float): Pareto-Radius of the data
        kernels (list): Data values at which ParetoDensity is measured, 
                        use pyplot.plot(kernels, paretoDensity) for display
        minAnzKernels (int): minimal number of kernels
    
    Returns:
        A dictionary containing the kernels, paretoDensity and the paretoRadius
    """
    if not isinstance(data, pd.Series):
        try:
            data = pd.Series(data)
        except:
            raise Exception("Data cannot be converted into pandas series")
    if not is_numeric_dtype(data):
        raise Exception("Data is not numeric!")
    
    data = data.apply(lambda x: np.nan if abs(x) == np.inf else x).dropna()
    values = data.unique()
    
    if (len(values) > 2) & (len(values) < 5):
        warnings.warn("Less than 5 unqiue values for density estimation. "
                      "Function may not work")
    
    if len(values) <= 2:
        warnings.warn('1 or 2 unique values for density estimation. Dirac '
                      'Delta distribution(s) is(are) assumed. Input of '
                      '"kernels", "paretoRadius" and "MinAnzKernels" or '
                      'ignored!')
        
        if (values[0] != 0):
            kernels = np.arange(values[0] * 0.9, 
                                values[0] * 1.1, 
                                values[0] * 0.0001)
        else:
            kernels = np.arange(values[0] - 0.1, 
                                values[0] + 0.1, 
                                0.0001)
        
        paretoDensity = np.zeros(len(kernels))
        intMidPoint = np.where(np.round(kernels, 4) \
                               == np.round(values[0], 4))[0][0]
        paretoDensity[intMidPoint] = 1
        
        paretoDensity = list(paretoDensity)
        kernels = list(kernels)
        
        if len(values) == 2:
            if (values[1] != 0):
                kernels2 = np.arange(values[1] * 0.9, 
                                     values[1] * 1.1, 
                                     values[1] * 0.0001)
            else:
                kernels2 = np.arange(values[1] - 0.1, 
                                     values[1] + 0.1, 
                                     0.0001)
            
            paretoDensity2 = np.zeros(len(kernels2))
            intMidPoint = np.where(np.round(kernels2, 4) \
                                   == np.round(values[1], 4))[0][0]
            paretoDensity2[intMidPoint] = 1
            
            paretoDensity2 = list(paretoDensity2)
            kernels = list(kernels)
            
            paretoDensity.extend(paretoDensity2)
            kernels.extend(kernels2)
        
        return {"kernels": kernels, "paretoDensity": paretoDensity, 
                "paretoRadius": 0}
    
    if len(data) < 10:
        warnings.warn("Less than 10 datapoints given, ParetoRadius "
                      "potientially cannot be calcualted.")
    
    if paretoRadius is None:
        paretoRadius = pareto_radius(data)
    if pd.isnull(paretoRadius) == True:
        paretoRadius = pareto_radius(data)
    if paretoRadius == 0:
        paretoRadius = pareto_radius(data)
    
    minData = data.min()
    maxData = data.max()
    
    if kernels is not None:
        nKernels = len(kernels)
    else:
        nKernels = 0
    
    if (kernels is None) or (kernels == 0) or (nKernels == 0) \
        or ((nKernels == 1) & (kernels[0] == 0)):
        nBins = optimal_no_bins(data)
        nBins = max(minAnzKernels , nBins)
        
        if nBins > 100:
            if nBins > 10000:
                nBins = 10000
                warnings.warn("Too many bins estimated, try to transform or "
                              "sample the data")
            else:
                nBins = nBins * 3 + 1
        
        breaks = pretty(minData, maxData, nBins)
        kernels = 0.5 * (breaks[1:] + breaks[:-1])
    
    if np.min(kernels) - paretoRadius > minData:
        kernels.append(minData)
    if np.max(kernels) + paretoRadius < maxData:
        kernels.append(maxData)
    kernels.sort()
    
    nKernels = len(kernels)
    # edge approximation
    # this data is at the lower edge
    lowData = data[data < (minData + paretoRadius)]
    lowR = 2 * minData - lowData
    # this data is at the upper edge
    upData = data[data > (maxData - paretoRadius)]
    upR = 2 * maxData - upData
    # extend data by mirrowing
    dataPlus = data.append(lowR).append(upR)
    
    paretoDensity = []
    for fltKernel in kernels:
        lb = fltKernel - paretoRadius
        ub = fltKernel + paretoRadius
        dataTemp = dataPlus[(dataPlus >= lb) & (dataPlus <= ub)]
        paretoDensity.append(len(dataTemp))
    
    area = np.trapz(paretoDensity, kernels)
    
    if (pd.isnull(area)) | (area < 0.0000000001):
        paretoDensity = [0 for x in range(nKernels)]
    else:
        paretoDensity = [x / area for x in paretoDensity]
    
    return {"kernels": kernels, "paretoDensity": paretoDensity, 
            "paretoRadius": paretoRadius}