# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 14:19:38 2019

@author: tinog
"""

import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from scipy.stats.mstats import mquantiles

def pareto_radius(data, maximumNrSamples = 10000, 
                  plotDistancePercentiles = False):
    """
    function calculates the Pareto-Radius for passed gauss mixture modell
    
    Args:
        data (dataframe, matrix): data array, cases in rows, 
                                  variables in columns
        maximumNrSamples (int): maximum number of samples (number of all array 
                                cells: number of rows * number of columns)
        plotDistancePercentiles (boolean): plot percentiles
    
    Returns:
        float value of Pareto-Radius
    """
    
    # convert data to pandas dataframe
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)._get_numeric_data()
    
    # replace inf by nan for checking issues
    data_check = data.copy()
    data_check[data_check == np.inf] = np.nan
    # check if nan are contained and warn
    if data_check.isnull().values.any() == True:
        warnings.warn("Data has nan or inf values, Pareto Radius may not be "\
                      "calculated")
    
    nData = data.shape[0] * data.shape[1]
    
    if nData <= maximumNrSamples:
        sampleData = data
    else:
        intSize = int(np.floor(maximumNrSamples / data.shape[1]))
        sampledIndex = np.sort(np.random.choice(list(data.index), 
                                                size=intSize, 
                                                replace=False))
        sampleData = data.loc[sampledIndex]
    
    # calculate distances
    distvec = pdist(sampleData)
    
    # selection of ParetoRadius
    paretoRadius = mquantiles(distvec, 18/100, alphap=1/3, betap=1/3)
    
    if paretoRadius == 0:
        pzt = pd.Series(mquantiles(distvec, [(x+1)/100 for x in range(100)], 
                                   alphap=1/3, betap=1/3)).dropna()
        paretoRadius = pzt[pzt > 0].min()
    
    # replace inf by nan for checiking issues
    psParetoCheck = pd.Series(paretoRadius)
    psParetoCheck = psParetoCheck\
    .apply(lambda x: np.nan if abs(x) == np.inf else x)
    
    # check result
    if psParetoCheck.isnull().values.any() == True:
        raise Exception("Pareto Radius could not be calculated. "
                        "(nan or inf values)")
    
    # todo plot
    if plotDistancePercentiles == True:
        pzt = pd.Series(mquantiles(distvec, [(x+1)/100 for x in range(100)], 
                                   alphap=1/3, betap=1/3)).dropna()
        pztPareto = pzt[pzt == paretoRadius[0]]
        pztParetoIndex = (list(pztPareto.index))[0] + 1
        plt.plot([x+1 for x in range(100)], pzt.values)
        plt.vlines(pztParetoIndex, 0, paretoRadius[0], color="red")
        plt.title("red = ParetoRadius")
        plt.xlabel("Percentiles")
        plt.ylabel("Distances")
        plt.show()
        
    
    # MT:
    # ALUs heuristik, in matlab in PDEplot, hier in dieser Funktion,
    # damit AdaptGauss die selbe Darstellung benutzt
    if nData > 1024:
        paretoRadius = paretoRadius * 4 / nData**0.2
    
    return paretoRadius[0]