# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:12:07 2019

@author: tinog_000
"""

import os
import pandas as pd

def load_examples():
    dctExamples = {}
    dctExamples["BimodalArtificial"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/BimodalArtificial.gz.pkl'), compression='gzip')
    dctExamples["MTY_Clipped"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/MTY_Clipped.gz.pkl'), compression='gzip')
    dctExamples["MuncipalIncomeTaxYield_IncomeTaxShare"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/MuncipalIncomeTaxYield_IncomeTaxShare.gz.pkl'), compression='gzip')
    dctExamples["SampleLogIncome"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/SampleLogInome.gz.pkl'), compression='gzip')
    dctExamples["SkewedDistribution"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/SkewedDistribution.gz.pkl'), compression='gzip')
    dctExamples["SkewedDistributionLongTable"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/SkewedDistributionLongTable.gz.pkl'), compression='gzip')
    dctExamples["StocksData2018Q1"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/StocksData2018Q1.gz.pkl'), compression='gzip')
    dctExamples["UniformSample"] = pd.read_pickle(os.path.join(os.path.dirname(__file__),'examples/UniformSample.gz.pkl'), compression='gzip')
    
    return dctExamples