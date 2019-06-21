# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:31:20 2019

@author: tinog_000
"""

import warnings
import pandas as pd
import numpy as np
import plotnine as p9
import unidip.dip as dip
from pandas.api.types import is_numeric_dtype
from scipy.stats.mstats import mquantiles
from scipy.stats import norm, trim_mean, skewtest, kstest
from helper.robust_normalization import robust_normalization
from helper.signed_log import signed_log
from helper.bimodal import bimodal
from helper.stat_pde_density import stat_pde_density

def md_plot(data, names=None, ordering='Default', scaling=None, 
            fill='darkblue', robustGaussian=True, gaussianColor='magenta', 
            gaussianLwd=1.5, boxPlot=False, boxColor='darkred', 
            mdScaling='width', size=0.01, 
            minimalAmountOfData=40, minimalAmountOfUniqueData=12, 
            sampleSize=500000, onlyPlotOutput=True):
    """
    Plots a mirrored density plot for each numeric column
    
    Args:
        data (dataframe): dataframe containing data. Each column is one 
                          variable
        names (list): list of column names (will be used if data is not a 
                      dataframe)
        ordering (str): 'Default', 'Columnwise', 'Alphabetical' or 'Statistics'
        scaling (str): scaling method, one of: Percentalize, CompleteRobust, 
                                               Robust, Log
        fill (str): color of MD-Plot
        robustGaussian (bool): draw a gaussian distribution if column is 
                               gaussian
        gaussianColor (str): color for gaussian distribution
        gaussianLwd (float): line width of gaussian distribution
        boxPlot (bool): draw box-plot
        boxColor (str): color for box-plots
        mdScaling (str): scale of ggplot violin
        size (float): line width of ggplot violin
        minimalAmountOfData (int): minimal number of rows
        minimalAmountOfUniqueData (int): minimal number of unique values per 
                                         column
        sampleSize (int): number of samples used if number of rows is larger 
                          than sampleSize
        onlyPlotOutput (bool): if True than returning only ggplot object,
                               if False than returning dictionary containing 
                               ggplot object and additional infos
        
    Returns:
        ggplot object or dictionary containing ggplot object and additional 
        infos
    """
    
    if not isinstance(data, pd.DataFrame):
        try:
            if names is not None:
                data = pd.DataFrame(data, columns = names)
            else:
                data = pd.DataFrame(data)
                lstCols = list(data.columns)
                dctCols = {}
                for strCol in lstCols:
                    dctCols[strCol] = "C_" + str(strCol)
                data = data.rename(columns=dctCols)
        except:
            raise Exception("Data cannot be converted into pandas dataframe")
    
    lstCols = list(data.columns)
    for strCol in lstCols:
        if not is_numeric_dtype(data[strCol]):
            print("Deleting non numeric column: " + strCol)
            data = data.drop([strCol], axis=1)
        else:
            if abs(data[strCol].sum()) == np.inf:
                print("Deleting infinite column: " + strCol)
                data = data.drop([strCol], axis=1)
    
    dvariables = data.shape[1]
    nCases = data.shape[0]
    
    if nCases > sampleSize:
        print('Data has more cases than "sampleSize". Drawing a sample for '
              'faster computation. You can omit this by setting '
              '"sampleSize=len(data)".')
        sampledIndex = np.sort(np.random.choice(list(data.index), 
                                                size=sampleSize, 
                                                replace=False))
        data = data.loc[sampledIndex]
    
    nPerVar = data.apply(lambda x: len(x.dropna()))
    nUniquePerVar = data.apply(lambda x: len(list(x.dropna().unique())))
    
    # renaming columns to nonumeric names
    lstCols = list(data.columns)
    dctCols = {}
    for strCol in lstCols:
        try:
            a = float(strCol)
            dctCols[strCol] = "C_" + str(strCol)
        except:
            dctCols[strCol] = str(strCol)
    data = data.rename(columns=dctCols)
    
    if scaling == "Percentalize":
        data = data.apply(lambda x: 100 * (x - x.min()) / (x.max() - x.min()))
    if scaling == "CompleteRobust":
        data = robust_normalization(data, centered=True, capped=True)
    if scaling == "Robust":
        data = robust_normalization(data, centered=False, capped=False)
    if scaling == "Log":
        data = signed_log(data, base="Ten")
        if robustGaussian == True:
            robustGaussian = False
            print("log with robust gaussian does not work, because mean and "
                  "variance is not valid description for log normal data")
    
#_______________________________________________Roboust Gaussian and Statistics
    if robustGaussian == True or ordering == "Statistics":
        data = data.applymap(lambda x: np.nan if abs(x) == np.inf else x)
        
        if nCases < 50:
            warnings.warn("Sample is maybe too small for statistical testing")
        
        factor = pd.Series([0.25, 0.75]).apply(lambda x: abs(norm.ppf(x)))\
        .sum()
        std = data.std()
        
        dfQuartile = data.apply(lambda x: mquantiles(x, [0.25, 0.75], 
                                                     alphap=0.5, betap=0.5))
        dfQuartile = dfQuartile.append(dfQuartile.loc[1] - dfQuartile.loc[0], 
                                       ignore_index=True)
        dfQuartile.index = ["low", "hi", "iqr"]
        dfMinMax = data.apply(lambda x: mquantiles(x, [0.001, 0.999], 
                                                   alphap=0.5, betap=0.5))
        dfMinMax.index = ["min", "max"]
        
        shat = pd.Series()
        mhat = pd.Series()
        nonunimodal = pd.Series()
        skewed = pd.Series()
        bimodalprob = pd.Series()
        isuniformdist = pd.Series()
        nSample = max([10000, nCases])
        normaldist = np.empty((nSample, dvariables))
        normaldist[:] = np.nan
        normaldist = pd.DataFrame(normaldist, columns=lstCols)
        
        for strCol in lstCols:
            shat[strCol] = min([std[strCol], 
                               dfQuartile[strCol].loc["iqr"] / factor])
            mhat[strCol] = trim_mean(data[strCol].dropna(), 0.1)
            
            if nCases > 45000 and nPerVar[strCol] > 8:
                # statistical testing does not work with to many cases
                sampledIndex = np.sort(np.random.choice(list(data.index), 
                                                size=45000, 
                                                replace=False))
                vec = data[strCol].loc[sampledIndex]
                if nUniquePerVar[strCol] > minimalAmountOfUniqueData:
                    nonunimodal[strCol] = dip.diptst(vec.dropna(), numt=100)[1]
                    skewed[strCol] = skewtest(vec)[1]
                    args = (dfMinMax[strCol].loc["min"], 
                            dfMinMax[strCol].loc["max"] \
                            - dfMinMax[strCol].loc["min"])
                    isuniformdist[strCol] = kstest(vec, "uniform", args)[1]
                    bimodalprob[strCol] = bimodal(vec)["Bimodal"]
                else:
                    print("Not enough unique values for statistical testing, "
                          "thus output of testing is ignored.")
                    nonunimodal[strCol] = 1
                    skewed[strCol] = 1
                    isuniformdist[strCol] = 0
                    bimodalprob[strCol] = 0
            elif nPerVar[strCol] < 8:
                warnings.warn("Sample of finite values to small to calculate "
                              "agostino.test or dip.test for " + strCol)
                nonunimodal[strCol] = 1
                skewed[strCol] = 1
                isuniformdist[strCol] = 0
                bimodalprob[strCol] = 0
            else:
                if nUniquePerVar[strCol] > minimalAmountOfUniqueData:
                    nonunimodal[strCol] = dip.diptst(data[strCol].dropna(), 
                                                                   numt=100)[1]
                    skewed[strCol] = skewtest(data[strCol])[1]
                    args = (dfMinMax[strCol].loc["min"], 
                            dfMinMax[strCol].loc["max"] \
                            - dfMinMax[strCol].loc["min"])
                    isuniformdist[strCol] = kstest(data[strCol], 
                                                   "uniform", args)[1]
                    bimodalprob[strCol] = bimodal(data[strCol])["Bimodal"]
                else:
                    print("Not enough unique values for statistical testing, "
                          "thus output of testing is ignored.")
                    nonunimodal[strCol] = 1
                    skewed[strCol] = 1
                    isuniformdist[strCol] = 0
                    bimodalprob[strCol] = 0
            
            if isuniformdist[strCol] < 0.05 and nonunimodal[strCol] > 0.05 \
            and skewed[strCol] > 0.05 and bimodalprob[strCol] < 0.05 \
            and nPerVar[strCol] > minimalAmountOfData \
            and nUniquePerVar[strCol] > minimalAmountOfUniqueData:
                normaldist[strCol] = np.random.normal(mhat[strCol], 
                                                      shat[strCol], 
                                                      nSample)
                normaldist[strCol] = normaldist[strCol]\
                .apply(lambda x: np.nan if x < data[strCol].min() \
                                 or x > data[strCol].max() else x)
        nonunimodal[nonunimodal == 0] = 0.0000000001
        skewed[skewed == 0] = 0.0000000001
        effectStrength = (-10 * np.log(skewed) - 10 * np.log(nonunimodal)) / 2
        
#______________________________________________________________________Ordering
    if ordering == "Default":
        bimodalprob = pd.Series()
        for strCol in lstCols:
            if nCases > 45000 and nPerVar[strCol] > 8:
                sampledIndex = np.sort(np.random.choice(list(data.index), 
                                                size=45000, 
                                                replace=False))
                vec = data[strCol].loc[sampledIndex]
                bimodalprob[strCol] = bimodal(vec)["Bimodal"]
            elif nPerVar[strCol] < 8:
                bimodalprob[strCol] = 0
            else:
                bimodalprob[strCol] = bimodal(data[strCol])["Bimodal"]
        if len(list(bimodalprob.unique())) < 2 and dvariables > 1 \
        and robustGaussian == True:
            rangfolge = list(effectStrength.sort_values(ascending=False).index)
            print("Using statistics for ordering instead of default")
        else:
            rangfolge = list(bimodalprob.sort_values(ascending=False).index)
    
    if ordering == "Columnwise":
        rangfolge = lstCols
    
    if ordering == "Alphabetical":
        rangfolge = lstCols.copy().sort()
    
    if ordering == "Statistics":
        rangfolge = list(effectStrength.sort_values(ascending=False).index)
    
#________________________________________________________________Data Reshaping
    if nPerVar.min() < minimalAmountOfData \
    or nUniquePerVar.min() < minimalAmountOfUniqueData:
        warnings.warn("Some columns have less than " + str(minimalAmountOfData)
                + " data points or less than " + str(minimalAmountOfUniqueData)
                     + " unique values. Changing from MD-plot to Jitter-Plot "
                     "for these columns.")
        dataDensity = data.copy()
        mm = data.median()
        for strCol in lstCols:
            if nPerVar[strCol] < minimalAmountOfData \
            or nUniquePerVar[strCol] < minimalAmountOfUniqueData:
                if mm[strCol] != 0:
                    dataDensity[strCol] = mm[strCol] \
                    * np.random.uniform(-0.001, 0.001, nCases) + mm[strCol]
                else:
                    dataDensity[strCol] = np.random.uniform(-0.001, 0.001, 
                                                            nCases)
        # Generates in the cases where pdf cannot be estimated a scatter plot
        dataJitter = dataDensity.copy()
        # Delete all scatters for features where distributions can be estimated
        for strCol in lstCols:
            if nPerVar[strCol] >= minimalAmountOfData \
            and nUniquePerVar[strCol] >= minimalAmountOfUniqueData:
                dataJitter[strCol] = np.nan
        #apply ordering
        dataframe = dataDensity[rangfolge].reset_index()\
        .melt(id_vars=["index"])
    else:
        dataframe = data[rangfolge].reset_index().melt(id_vars=["index"])
    
    dctCols = {"index": "ID", "variable": "Variables", "value": "Values"}
    dataframe = dataframe.rename(columns=dctCols)
    #return dataframe, rangfolge, normaldist, dctCols
    
#______________________________________________________________________Plotting
    plot = p9.ggplot(dataframe, p9.aes(x="Variables", group="Variables", 
                                        y="Values")) \
                     + p9.scale_x_discrete(limits=rangfolge)
    
    plot = plot + p9.geom_violin(stat = stat_pde_density(), fill=fill, 
                           scale=mdScaling, size=size, trim=True) \
                           + p9.theme(axis_text_x=p9.element_text(rotation=90))
    
    if nPerVar.min() < minimalAmountOfData \
    or nUniquePerVar.min() < minimalAmountOfUniqueData:
        dataframejitter = dataJitter[rangfolge].reset_index()\
        .melt(id_vars=["index"])
        dataframejitter = dataframejitter.rename(columns=dctCols)
        plot = plot + p9.geom_jitter(size=2, data=dataframejitter, 
                                     mapping= p9.aes(x="Variables", 
                                                     group="Variables", 
                                                     y="Values"), 
                                     position=p9.position_jitter(0.15))
    
    if robustGaussian == True:
        dfTemp = normaldist[rangfolge].reset_index().melt(id_vars=["index"])
        dfTemp = dfTemp.rename(columns=dctCols)
        if dfTemp["Values"].isnull().all() == False:
            plot = plot + p9.geom_violin(data = dfTemp, 
                                         mapping = p9.aes(x="Variables", 
                                                          group="Variables", 
                                                          y="Values"), 
                                         colour=gaussianColor, alpha=0, 
                                         scale=mdScaling, size=gaussianLwd, 
                                         na_rm=True, trim=True, fill=None, 
                                         position="identity", width=1)
    
    if boxPlot == True:
        plot = plot + p9.stat_boxplot(geom = "errorbar", width = 0.5, 
                                      color=boxColor) \
                    + p9.geom_boxplot(width=1, outlier_colour = None, alpha=0, 
                                      fill='#ffffff', color=boxColor, 
                                      position="identity")
    
    if onlyPlotOutput == True:
        return plot
    else:
        print(plot)
        return {"Ordering": rangfolge, "DataOrdered": data[rangfolge], 
                "ggplotObj": plot}