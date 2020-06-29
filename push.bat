ECHO ON
echo Push the changes
git add -A
git status
git commit -m "data update"
git push heroku master
git push origin master
