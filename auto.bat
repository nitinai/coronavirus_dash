ECHO ON
echo Running auto script
d:
cd D:\workdir\ML\ml_units\kaggle\Vis\coronavirus\Dashboard\coronavirus_dash
cd data_sources\COVID-19
git pull
cd ..\..
python utils_update_data.py --d True
python utils_update_data.py --p True
start heroku local web -f Procfile.Windows
timeout 6
start "" http://127.0.0.1:5000/
push.bat
PAUSE
