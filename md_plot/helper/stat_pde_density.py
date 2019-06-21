# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 12:30:49 2019

@author: tinog_000
"""

import warnings
import pandas as pd
import numpy as np
import plotnine as p9
from .pareto_density_estimation import pareto_density_estimation

class stat_pde_density(p9.stats.stat.stat):
    DEFAULT_PARAMS = {'geom': 'violin', 'position': 'dodge',
                      'na_rm': True,
                      'adjust': 1, 'kernel': 'gaussian',
                      'n': 1024, 'trim': True,
                      'scale': 'area'}
    
    @classmethod
    def compute_group(self, data, scales, **params):
        def compute_pdedensity(x):
            nx = len(x)
            if nx < 2:
                warnings.warn("stat_pde_density: Groups with fewer than two "\
                              "data points have been dropped.")
                return pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan]], 
                                    columns=["x", "density", "scaled", 
                                             "count", "n"])
            
            flag = False
            if len(list(x.unique())) == 1:
                warnings.warn("stat_pde_density: Only one unique value in "\
                              "Data.")
                x = pd.Series([x.iloc[0], 
                               x.iloc[0] * np.random.uniform(0.999, 1.001)])
                flag = True
            
            dens = pareto_density_estimation(x)
            
            if flag == True:
                dens["kernels"] = pd.Series(dens["kernels"])\
                .apply(lambda x: x * np.random.uniform(0.998, 1.002))
                y = dens["kernels"].max() - dens["kernels"].min()
                dens["paretoDensity"] = pd.Series(dens["paretoDensity"])\
                .apply(lambda x: 1 / y)
            
            dfReturn = pd.DataFrame(dens["kernels"], columns=["x"])
            dfReturn["density"] = dens["paretoDensity"]
            dfReturn["scaled"] = dens["paretoDensity"] \
            / max(dens["paretoDensity"])
            dfReturn["count"] = dfReturn["density"] * nx
            dfReturn["n"] = nx
            return dfReturn
        
        dens = compute_pdedensity(data["y"])
        dens["y"] = dens["x"]
        dens["x"] = data["x"].mean()
        dens["width"] = 0.9
        
        if params["scale"] == "area":
            dens["violinwidth"] = dens["density"] / dens["density"].max()
        if params["scale"] == "count":
            dens["violinwidth"] = (dens["density"] / dens["density"].max()) \
            * (dens["n"] / dens["n"].max())
        if params["scale"] == "width":
            dens["violinwidth"] = dens["scaled"]
        
        return dens