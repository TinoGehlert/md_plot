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
from .helper.robust_normalization import robust_normalization
from .helper.signed_log import signed_log
from .helper.bimodal import bimodal
from .helper.stat_pde_density import stat_pde_density

def MDplot(Data, Names=None, Ordering='Default', Scaling=None, 
           Fill='darkblue', RobustGaussian=True, GaussianColor='magenta', 
           GaussianLwd=1.5, BoxPlot=False, BoxColor='darkred', 
           MDscaling='width', Size=0.01, 
           MinimalAmoutOfData=40, MinimalAmoutOfUniqueData=12, 
           SampleSize=500000, OnlyPlotOutput=True, 
           ValueColumn=None, ClassColumn=None):
    """
    Plots a mirrored density plot for each numeric column
    
    Args:
        Data (dataframe): dataframe containing data. Each column is one 
                          variable (wide table format, for long table format 
                          see ValueColumn and ClassColumn)
        Names (list): list of column names (will be used if data is not a 
                      dataframe)
        Ordering (str): 'Default', 'Columnwise', 'Alphabetical' or 'Statistics'
        Scaling (str): scaling method, one of: Percentalize, CompleteRobust, 
                                               Robust, Log
        Fill (str): color of MD-Plot
        RobustGaussian (bool): draw a gaussian distribution if column is 
                               gaussian
        GaussianColor (str): color for gaussian distribution
        GaussianLwd (float): line width of gaussian distribution
        BoxPlot (bool): draw box-plot
        BoxColor (str): color for box-plots
        MDscaling (str): scale of ggplot violin
        Size (float): line width of ggplot violin
        MinimalAmoutOfData (int): minimal number of rows
        MinimalAmoutOfUniqueData (int): minimal number of unique values per 
                                         column
        SampleSize (int): number of samples used if number of rows is larger 
                          than SampleSize
        OnlyPlotOutput (bool): if True than returning only ggplot object,
                               if False than returning dictionary containing 
                               ggplot object and additional infos
        ValueColumn (str): name of the column of values to be plotted
                           (data in long table format)
        ClassColumn (str): name of the column with class identifiers for the 
                           value column (data in long table format)
        
    Returns:
        ggplot object or dictionary containing ggplot object and additional 
        infos
    """
    
    if not isinstance(Data, pd.DataFrame):
        try:
            if Names is not None:
                Data = pd.DataFrame(Data, columns = Names)
            else:
                Data = pd.DataFrame(Data)
                lstCols = list(Data.columns)
                dctCols = {}
                for strCol in lstCols:
                    dctCols[strCol] = "C_" + str(strCol)
                Data = Data.rename(columns=dctCols)
        except:
            raise Exception("Data cannot be converted into pandas dataframe")
    
    if ValueColumn is not None and ClassColumn is not None:
        lstCols = list(Data.columns)
        if ValueColumn not in lstCols:
            raise Exception("ValueColumn not contained in dataframe")
        if ClassColumn not in lstCols:
            raise Exception("ClassColumn not contained in dataframe")
        
        lstClasses = list(Data[ClassColumn].unique())
        DataWide = pd.DataFrame()
        for strClass in lstClasses:
            if len(DataWide) == 0:
                DataWide = Data[Data[ClassColumn] == strClass].copy()\
                .reset_index(drop=True)
                DataWide = DataWide.rename(columns={ValueColumn: strClass})
                DataWide = DataWide[[strClass]]
            else:
                dfTemp = Data[Data[ClassColumn] == strClass].copy()\
                .reset_index(drop=True)
                dfTemp = dfTemp.rename(columns={ValueColumn: strClass})
                dfTemp = dfTemp[[strClass]]
                DataWide = DataWide.join(dfTemp, how='outer')
        Data = DataWide.copy()
    
    lstCols = list(Data.columns)
    for strCol in lstCols:
        if not is_numeric_dtype(Data[strCol]):
            print("Deleting non numeric column: " + strCol)
            Data = Data.drop([strCol], axis=1)
        else:
            if abs(Data[strCol].sum()) == np.inf:
                print("Deleting infinite column: " + strCol)
                Data = Data.drop([strCol], axis=1)
    
    Data = Data.rename_axis("index", axis="index")\
    .rename_axis("variable", axis="columns")
    dvariables = Data.shape[1]
    nCases = Data.shape[0]
    
    if nCases > SampleSize:
        print('Data has more cases than "SampleSize". Drawing a sample for '
              'faster computation. You can omit this by setting '
              '"SampleSize=len(data)".')
        sampledIndex = np.sort(np.random.choice(list(Data.index), 
                                                size=SampleSize, 
                                                replace=False))
        Data = Data.loc[sampledIndex]
    
    nPerVar = Data.apply(lambda x: len(x.dropna()))
    nUniquePerVar = Data.apply(lambda x: len(list(x.dropna().unique())))
    
    # renaming columns to nonumeric names
    lstCols = list(Data.columns)
    dctCols = {}
    for strCol in lstCols:
        try:
            a = float(strCol)
            dctCols[strCol] = "C_" + str(strCol)
        except:
            dctCols[strCol] = str(strCol)
    Data = Data.rename(columns=dctCols)
    
    if Scaling == "Percentalize":
        Data = Data.apply(lambda x: 100 * (x - x.min()) / (x.max() - x.min()))
    if Scaling == "CompleteRobust":
        Data = robust_normalization(Data, centered=True, capped=True)
    if Scaling == "Robust":
        Data = robust_normalization(Data, centered=False, capped=False)
    if Scaling == "Log":
        Data = signed_log(Data, base="Ten")
        if RobustGaussian == True:
            RobustGaussian = False
            print("log with robust gaussian does not work, because mean and "
                  "variance is not valid description for log normal data")
    
#_______________________________________________Roboust Gaussian and Statistics
    if RobustGaussian == True or Ordering == "Statistics":
        Data = Data.applymap(lambda x: np.nan if abs(x) == np.inf else x)
        
        if nCases < 50:
            warnings.warn("Sample is maybe too small for statistical testing")
        
        factor = pd.Series([0.25, 0.75]).apply(lambda x: abs(norm.ppf(x)))\
        .sum()
        std = Data.std()
        
        dfQuartile = Data.apply(lambda x: mquantiles(x, [0.25, 0.75], 
                                                     alphap=0.5, betap=0.5))
        dfQuartile = dfQuartile.append(dfQuartile.loc[1] - dfQuartile.loc[0], 
                                       ignore_index=True)
        dfQuartile.index = ["low", "hi", "iqr"]
        dfMinMax = Data.apply(lambda x: mquantiles(x, [0.001, 0.999], 
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
            mhat[strCol] = trim_mean(Data[strCol].dropna(), 0.1)
            
            if nCases > 45000 and nPerVar[strCol] > 8:
                # statistical testing does not work with to many cases
                sampledIndex = np.sort(np.random.choice(list(Data.index), 
                                                size=45000, 
                                                replace=False))
                vec = Data[strCol].loc[sampledIndex]
                if nUniquePerVar[strCol] > MinimalAmoutOfUniqueData:
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
                if nUniquePerVar[strCol] > MinimalAmoutOfUniqueData:
                    nonunimodal[strCol] = dip.diptst(Data[strCol].dropna(), 
                                                                   numt=100)[1]
                    skewed[strCol] = skewtest(Data[strCol])[1]
                    args = (dfMinMax[strCol].loc["min"], 
                            dfMinMax[strCol].loc["max"] \
                            - dfMinMax[strCol].loc["min"])
                    isuniformdist[strCol] = kstest(Data[strCol], 
                                                   "uniform", args)[1]
                    bimodalprob[strCol] = bimodal(Data[strCol])["Bimodal"]
                else:
                    print("Not enough unique values for statistical testing, "
                          "thus output of testing is ignored.")
                    nonunimodal[strCol] = 1
                    skewed[strCol] = 1
                    isuniformdist[strCol] = 0
                    bimodalprob[strCol] = 0
            
            if isuniformdist[strCol] < 0.05 and nonunimodal[strCol] > 0.05 \
            and skewed[strCol] > 0.05 and bimodalprob[strCol] < 0.05 \
            and nPerVar[strCol] > MinimalAmoutOfData \
            and nUniquePerVar[strCol] > MinimalAmoutOfUniqueData:
                normaldist[strCol] = np.random.normal(mhat[strCol], 
                                                      shat[strCol], 
                                                      nSample)
                normaldist[strCol] = normaldist[strCol]\
                .apply(lambda x: np.nan if x < Data[strCol].min() \
                                 or x > Data[strCol].max() else x)
        nonunimodal[nonunimodal == 0] = 0.0000000001
        skewed[skewed == 0] = 0.0000000001
        effectStrength = (-10 * np.log(skewed) - 10 * np.log(nonunimodal)) / 2
        
#______________________________________________________________________Ordering
    if Ordering == "Default":
        bimodalprob = pd.Series()
        for strCol in lstCols:
            if nCases > 45000 and nPerVar[strCol] > 8:
                sampledIndex = np.sort(np.random.choice(list(Data.index), 
                                                size=45000, 
                                                replace=False))
                vec = Data[strCol].loc[sampledIndex]
                bimodalprob[strCol] = bimodal(vec)["Bimodal"]
            elif nPerVar[strCol] < 8:
                bimodalprob[strCol] = 0
            else:
                bimodalprob[strCol] = bimodal(Data[strCol])["Bimodal"]
        if len(list(bimodalprob.unique())) < 2 and dvariables > 1 \
        and RobustGaussian == True:
            rangfolge = list(effectStrength.sort_values(ascending=False).index)
            print("Using statistics for ordering instead of default")
        else:
            rangfolge = list(bimodalprob.sort_values(ascending=False).index)
    
    if Ordering == "Columnwise":
        rangfolge = lstCols
    
    if Ordering == "Alphabetical":
        rangfolge = lstCols.copy()
        rangfolge.sort()
    
    if Ordering == "Statistics":
        rangfolge = list(effectStrength.sort_values(ascending=False).index)
    
#________________________________________________________________Data Reshaping
    if nPerVar.min() < MinimalAmoutOfData \
    or nUniquePerVar.min() < MinimalAmoutOfUniqueData:
        warnings.warn("Some columns have less than " + str(MinimalAmoutOfData)
                + " data points or less than " + str(MinimalAmoutOfUniqueData)
                     + " unique values. Changing from MD-plot to Jitter-Plot "
                     "for these columns.")
        dataDensity = Data.copy()
        mm = Data.median()
        for strCol in lstCols:
            if nPerVar[strCol] < MinimalAmoutOfData \
            or nUniquePerVar[strCol] < MinimalAmoutOfUniqueData:
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
            if nPerVar[strCol] >= MinimalAmoutOfData \
            and nUniquePerVar[strCol] >= MinimalAmoutOfUniqueData:
                dataJitter[strCol] = np.nan
        #apply ordering
        dataframe = dataDensity[rangfolge].reset_index()\
        .melt(id_vars=["index"])
    else:
        dataframe = Data[rangfolge].reset_index().melt(id_vars=["index"])
    
    dctCols = {"index": "ID", "variable": "Variables", "value": "Values"}
    dataframe = dataframe.rename(columns=dctCols)
    
#______________________________________________________________________Plotting
    plot = p9.ggplot(dataframe, p9.aes(x="Variables", group="Variables", 
                                        y="Values")) \
                     + p9.scale_x_discrete(limits=rangfolge)
    
    plot = plot + p9.geom_violin(stat = stat_pde_density(scale=MDscaling), 
                                 fill=Fill, size=Size, trim=True) \
                           + p9.theme(axis_text_x=p9.element_text(rotation=90))
    
    if nPerVar.min() < MinimalAmoutOfData \
    or nUniquePerVar.min() < MinimalAmoutOfUniqueData:
        dataframejitter = dataJitter[rangfolge].reset_index()\
        .melt(id_vars=["index"])
        dataframejitter = dataframejitter.rename(columns=dctCols)
        plot = plot + p9.geom_jitter(size=2, data=dataframejitter, 
                                     mapping= p9.aes(x="Variables", 
                                                     group="Variables", 
                                                     y="Values"), 
                                     position=p9.position_jitter(0.15))
    
    if RobustGaussian == True:
        dfTemp = normaldist[rangfolge].reset_index().melt(id_vars=["index"])
        dfTemp = dfTemp.rename(columns=dctCols)
        if dfTemp["Values"].isnull().all() == False:
            plot = plot + p9.geom_violin(data = dfTemp, 
                                         mapping = p9.aes(x="Variables", 
                                                          group="Variables", 
                                                          y="Values"), 
                                         colour=GaussianColor, alpha=0, 
                                         scale=MDscaling, size=GaussianLwd, 
                                         na_rm=True, trim=True, fill=None, 
                                         position="identity", width=1)
    
    if BoxPlot == True:
        plot = plot + p9.stat_boxplot(geom = "errorbar", width = 0.5, 
                                      color=BoxColor) \
                    + p9.geom_boxplot(width=1, outlier_colour = None, alpha=0, 
                                      fill='#ffffff', color=BoxColor, 
                                      position="identity")
    
    if OnlyPlotOutput == True:
        return plot
    else:
        print(plot)
        return {"Ordering": rangfolge, "DataOrdered": Data[rangfolge], 
                "ggplotObj": plot}