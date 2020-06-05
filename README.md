# Coronavirus COVID-19 Dashboard

Please check out at https://covid19updates.herokuapp.com

## Installation instructions

* Install Anaconda python 3.7

* Create a new conda environment and install the required packages
  * `conda create -n nitinai python=3.7.3`
  * `conda activate nitinai`
  * `python -m pip install -r requirements.txt`

## Daily Updates
  * `git pull` the global data in `./data_sources/COVID-19`
  * `python utils_update_data.py --d True`
  * `python utils_update_data.py --p True`
  * `heroku local web -f Procfile.Windows`
  *  Test at http://127.0.0.1:8050/
  *  push the data with `push.bat`



## TODO
- Doubling rate
- Total cases / 1M pop
- Total Deaths / 1M pop
- Outcome of cases (% of recoveries vs deaths)


## Performance improvement
> This doesn't worked very well. The pickle file of all country accumlates big in size. Even performance degraded.
    - utils_offline_plots : create and pickle the plotly figures
    - app : just load the pickled figure and render

> beta_1.py : separate callbacks for each graph
    - Slight improvement.
    - utils_graphs.py has all the graph plotting functions.
    - utils_comman.py has global variables
    - utils_update_data.py : downloads India data and merge it with global data
    - The selected country was cached in hidden html tag. Initially the datatable has
        a issue with getting the row selection. This is causing further issues as the 
        selected country is not getting set in html tag.





