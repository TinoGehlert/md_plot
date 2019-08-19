.. MD-plot documentation master file, created by
   sphinx-quickstart on Mon Aug 19 11:41:29 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MD-plot's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This function creates a MD-plot for each column of the dataframe. The MD-plot is a visualization
for a boxplot-like Shape of the PDF published in [Thrun/Ultsch, 2019]. It is an improvement of
violin or so-called bean plots and posses advantages in comparison to the conventional well-known
box plot [Thrun/Ultsch, 2019]. This is the Python implementation of the function MD-Plot contained 
in R package DataVisualizations_.

.. _DataVisualizations: https://cran.r-project.org/web/packages/DataVisualizations/index.html

Basic Usage
^^^^^^^^^^^

from md_plot import MDplot, load_examples

dctExamples = load_examples()

MDplot(dctExamples["BimodalArtificial"])



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
