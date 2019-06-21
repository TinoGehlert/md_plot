# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 10:48:05 2019

@author: tinog
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from scipy.signal import lfilter
from scipy.stats.mstats import mquantiles
from scipy.stats import norm

def bimodal(data, plotIt=False, narm=True):
    """
    Estimation if empirical data distribution has two modes
    Reimplementation of R (Michael Thrun) which is reimplemented from matlab 
    of ALU 2006
    
    Args:
        data (series): one dimensial data vector
        plotIt (boolean): plot the function with convex & concave parts
        narm (boolean): drop nan and inf values
    
    Returns:
        dictionary containing:
            Bimodal: in [0,1] indication (probability) whether Data is bimodal
            ProConvex: (longest successive part where SecondDerivative>0) / n 
                                                                        * 100
            ProConcave: (longest successive part where SecondDerivative<0) / n 
                                                                        * 100
    """
    
    def convex_concave(x, fx, plotIt=False):
        """
        Estimate if a function is convex or concave
        
        Args:
            x (series / array): x values of function
            fx (series / array): correponding y values
            plotIt (boolean): plot the function with convex & concave parts
        
        Returns:
            dictionary containing:
                Kruemmung: (ProConvex-ProConcave)/n*100
                ProConvex: (longest successive part where SecondDerivative>0)
                                                                        /n *100
                ProConcave: (longest successive part where SecondDerivative<0)
                                                                        /n *100
                SecondDerivative: finite and filtered approximation to second 
                                  derivative of f(x)
                ErsteAbleitung: finite and filtered approximation to first 
                                derivaive of f(x)
        """
        # converting to series
        if not isinstance(x, pd.Series):
            x = pd.Series(x)
        if not isinstance(fx, pd.Series):
            fx = pd.Series(fx)
        
        # constants
        EPS = 1.5  # minimal Kruemmung > 0
        
        anz = len(x)
        
        ersteAbleitung = fx.diff().dropna() / x.diff().dropna()
        ersteAbleitung = pd.Series([0]).append(ersteAbleitung)
        windowSize = 13
        ersteAbleitung = pd.Series(lfilter(np.repeat(1.0/windowSize, 
                                                     windowSize), 
                                           1, ersteAbleitung))
        
        secondDerivative = ersteAbleitung.diff().dropna() / x.diff().dropna()
        secondDerivative = pd.Series([0]).append(secondDerivative)
        windowSize = 15
        secondDerivative = pd.Series(lfilter(np.repeat(1.0/windowSize, 
                                                       windowSize), 
                                             1, secondDerivative))
        
        Next = pd.Series([x for x in range(1, anz)]).append(pd.Series([anz-1]))
        posOrNeg = x * 0
        posOrNeg[secondDerivative >  EPS] = 1
        posOrNeg[secondDerivative < -1 * EPS] = -1
        # NextIdentical is true if the next is on the same side
        nextIdentical = posOrNeg == posOrNeg[Next].reset_index(drop=True)
        posRuns = nextIdentical & (secondDerivative > EPS)
        negRuns =  nextIdentical & (secondDerivative < -1 * EPS)
        
        maxPosRunLength = 0
        posRunLength = 0
        maxNegRunLength = 0
        negRunLength = 0
        for i in list(range(anz)):
            if posRuns[i] == True:
                posRunLength += 1
            else:
                posRunLength = 0
            if negRuns[i] == True:
                negRunLength += 1
            else:
                negRunLength = 0
            maxPosRunLength = max([maxPosRunLength, posRunLength])
            maxNegRunLength = max([maxNegRunLength, negRunLength])
        
        proConvex  = 100 * maxPosRunLength / anz
        proConcave = 100 * maxNegRunLength / anz
        kruemmung  = 100 * (proConvex - proConcave) / anz
        
        if plotIt == True:
            plt.plot(x, fx, c='blue')
            plt.xlabel('x \n green = convex, red = concave')
            plt.ylabel('f(x)')
            plt.scatter(x[posRuns == True], fx[posRuns == True], 
                        c='green', s=20)
            plt.scatter(x[negRuns == True], fx[negRuns == True], 
                        c='red', s=20)
        
        return {"Kruemmung": kruemmung, "ProConvex": proConvex, 
                "ProConcave": proConcave, "SecondDerivative": secondDerivative,
                "ErsteAbleitung": ersteAbleitung}
    
    
    if not isinstance(data, pd.Series):
        try:
            data = pd.Series(data)
        except:
            raise Exception("Data cannot be converted into pandas series")
    if not is_numeric_dtype(data):
        raise Exception("Data is not numeric!")
    
    data = data.apply(lambda x: np.nan if abs(x) == np.inf else x).dropna()
    
    fx = pd.Series(mquantiles(data, [x / 100 for x in range(1,100)], 
                                     alphap=0.5, betap=0.5)).dropna()
    percent = np.arange(0.01, 1, 0.01)
    x = norm.ppf(percent)
    dctV = convex_concave(x, fx, plotIt)
    bimodal = norm.cdf(min(dctV["ProConvex"], dctV["ProConcave"]), 7, 3)
    
    if plotIt == True:
        plt.title('Bimodal = ' + str(round(bimodal, 3) * 100) \
                  + " | ProConvex = " + str(round(dctV["ProConvex"], 2)) \
                  + " | ProConcave = " + str(round(dctV["ProConcave"], 2)))
        plt.show()
    
    return {"Bimodal": bimodal, "ProConvex": dctV["ProConvex"], 
            "ProConcave": dctV["ProConcave"]}