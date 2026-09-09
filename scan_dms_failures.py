@"
protocol=https
host=ccoe-gitlab.hii-tsd.com

"@ | git credential-manager erase

git fetch origin


git pull origin main


git switch -c jay-irc_census_report_clean
