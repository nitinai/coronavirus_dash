web: gunicorn --workers 6 --threads 2 app:server
#I’ve set processes=6 in app.run_server so that multiple callbacks can be executed in parallel. 
#In production, this is done with something like $ gunicorn --workers 6 --threads 2 app:server
# https://community.plotly.com/t/working-on-large-datasets-comparison-with-shiny/6199/4
