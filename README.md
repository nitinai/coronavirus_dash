# Coronavirus COVID-19 Dashboard

Please check out at https://covid19updates.herokuapp.com

## Installation instructions

* Install Anaconda python 3.7

* Create a new conda environment and install the required packages
  * `conda create -n dashboard python=3.7.3`
  * `conda activate dashboard`
  * `python -m pip install -r requirements.txt`

## How to update the dashboard with daily data
  * `git pull` the global data in `./data_sources/COVID-19`
  * `python utils_update_data.py --d True`
  * `python utils_update_data.py --p True`
  * `heroku local web -f Procfile.Windows`
  *  Test at http://127.0.0.1:8050/
  *  push the data with `push.bat`


* Please open an issue if you find a bug
