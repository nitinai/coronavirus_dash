ECHO ON
echo Running auto script
cd data_sources\COVID-19
git pull
cd ..\..
python utils_update_data.py --d True
python utils_update_data.py --p True
push.bat
PAUSE
