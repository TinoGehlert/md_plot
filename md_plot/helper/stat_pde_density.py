# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 12:30:49 2019

@author: tinog_000
"""

import warnings
import pandas as pd
import numpy as np
from plotnine.stats.stat import stat
from plotnine.exceptions import PlotnineError
from .pareto_density_estimation import pareto_density_estimation

class stat_pde_density(stat):
    REQUIRED_AES = {'x', 'y'}
    NON_MISSING_AES = {'weight'}
    DEFAULT_PARAMS = {'geom': 'violin', 'position': 'dodge',
                      'na_rm': True,
                      'adjust': 1, 'kernel': 'gaussian',
                      'n': 1024, 'trim': True,
                      'scale': 'area'}
    DEFAULT_AES = {'weight': None}
    CREATES = {'width'}
    
    def setup_params(self, data):
        params = self.params.copy()
        
        valid_scale = ('area', 'count', 'width')
        if params['scale'] not in valid_scale:
            msg = "Parameter scale should be one of {}"
            raise PlotnineError(msg.format(valid_scale))
            
        return params
    
    @classmethod
    def compute_panel(cls, data, scales, **params):
        data = super(cls, cls).compute_panel(data, scales, **params)

        if not len(data):
            return data

        if params['scale'] == 'area':
            data['violinwidth'] = data['density']/data['density'].max()
        elif params['scale'] == 'count':
            data['violinwidth'] = (data['density'] /
                                   data['density'].max() *
                                   data['n']/data['n'].max())
        elif params['scale'] == 'width':
            data['violinwidth'] = data['scaled']

        return data
    
    @classmethod
    def compute_group(cls, data, scales, **params):
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
        
        return dens