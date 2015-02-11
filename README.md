# lostfilm-rss-parser

1. edit <b>config.yml</b> 
   - add your series
   - add your lostfilm cookie
   - change path to torrents dir - option 'downloads-path'
   - change transmission auth data, if you want to use automatic transmission download
   - enable transmission connect - option 'use_transmission'
   - change email sending data and enable it - option 'send_email' -  if you want
   - change path to store torrent file - options 'store_torrent_files' and 'torrents-path' - for storing torrent files. crontab user must have write permissions to this dir
   - if you want - change user agent
2. edit <b>run.sh</b> - change path to parser dir
3. make <b>parser.py</b> and <b>run.sh</b> executable (chmod +x)
4. make lostfilm-rss-parser dir writable for crontab user - it's needed for storing log files
5. add <b>run.sh</b> to your crontab
