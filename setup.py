from setuptools import setup, find_packages


setup(name='md_plot',
      version='0.2.0',
      project_urls={'R-Version': 'https://cran.r-project.org/web/packages/DataVisualizations/index.html', 
                    'Source': 'https://github.com/TinoGehlert/md_plot', 
                    'Docs': 'https://md-plot.readthedocs.io'},
      description='Draws a mirrored density plot for each input column',
      long_description=open('readme_pypi.rst').read(),
      download_url='https://github.com/TinoGehlert/md_plot/archive/v0.2.0.tar.gz',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
      ],
      keywords='data_science violin density_plot',
      author='TinoGehlert',
      author_email='tinogehlert@aol.com',
      license='GNU General Public License v3 (GPLv3)',
      packages=find_packages(),
      install_requires=[
          'pandas>=0.24.2',
          'numpy>=1.16',
          'scipy>=1.1.0',
          'matplotlib>=3.1.0',
          'plotnine>=0.5.1',
      ],
      include_package_data=True,
      zip_safe=False)