# Mirrored Density Plot - MD-Plot

[![Documentation Status](https://readthedocs.org/projects/md-plot/badge/?version=latest)](https://md-plot.readthedocs.io/en/latest/?badge=latest)

## What is it
This function creates a MD-plot for each column of the dataframe. The MD-plot is a visualization
for a boxplot-like Shape of the PDF published in [Thrun/Ultsch, 2019]. It is an improvement of
violin or so-called bean plots and posses advantages in comparison to the conventional well-known
box plot [Thrun/Ultsch, 2019]. This is the Python implementation of the function MD-Plot contained 
in R package [DataVisualizations](https://cran.r-project.org/web/packages/DataVisualizations/index.html)

## Where to get it
The source code is hosted on GitHub at: https://github.com/TinoGehlert/md_plot

```sh
pip install md_plot
```

## Basic Usage
```python
from md_plot import MDplot, load_examples

dctExamples = load_examples()

MDplot(dctExamples["BimodalArtificial"])
```

<div align="left">
  <img src="https://github.com/TinoGehlert/md_plot/blob/master/doc/images/bimodal_artificial.png"><br>
</div>

## Dependencies
- [pandas](https://pandas.pydata.org): 0.24.2 or higher
- [NumPy](http://www.numpy.org): 1.16.0 or higher
- [scipy](https://www.scipy.org/): 1.1.0 or higher
- [matplotlib](https://matplotlib.org/): 3.1.0 or higher
- [plotnine](https://plotnine.readthedocs.io/en/stable/): 0.5.1 or higher
- [unidip](https://github.com/BenjaminDoran/unidip/): 0.1.1 or higher

Windows users of Anaconda distribution should update numpy, scipy and matplotlib via conda instead of pip.