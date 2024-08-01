# Search Engine Scraping Coding Challenge

This project is specifically developed solely for Cargobase coding challenge.


## Dependencies
+ Flask Micro Framework 1.1.0
+ Flask SQLAlchemy
+ Flask Redis
+ Flask WTF
+ Requests library
+ LXML
+ RQ library
+ UWSGI

# What can be improved
Since this app written in very short time, here are the list what can be improved in the future:

- Using proxy IPs to scrape to reduce chances being blocked by search engine
- Implement RQ Dashboard for monitoring failing & restarting failing jobs
- Adding more UserAgents list
- Sanitizing "keyword"
- Adding Unittest
- Securing Redis Server
- Conditional DOM Parsing to cater for eg: Google Rich Snippet Result
- Adding Docker Compose and Dockerfile for each container
# Getting start
1. Clone Repository to your local / server folder
```
git clone https://github.com/bsalim/cargobase-coding-challenge.git
```

2. Create .env file to the ROOT PATH
```
ENV=development
FLASK_ENV=development
SECRET_KEY=<YOUR_SECRET_KEY>
DEBUG=True
DB_NAME=<YOUR_DB_NAME>
DB_USER=<YOUR_DB_USER>
DB_PASS=<YOUR_DB_PASS>
DB_HOST=<YOUR_DB_HOST>
REDISTOGO_URL = redis://localhost:6379
```

3. Install Dependencies
```
pip install -r requirements.txt
```

# Deployment


## Supervisor
```
supervisorctl start cargobase
```
App supervisor config file
```
[program:cargobase]
environment =
   FLASK_APP=run.py,
   FLASK_ENV=production

command=/var/www/cargobase/venv/bin/uwsgi --ini /var/www/cargobase/uwsgi.ini
directory=/var/www/cargobase/
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
```

##### Worker supervisor config file
You can run using
```
supervisorctl start worker
```
```
[program:worker]
environment =
   FLASK_ENV=production

command=/var/www/cargobase/venv/bin/uwsgi --ini /var/www/cargobase/worker.ini
directory=/var/www/cargobase/
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
```

## app.ini (application UWSGI file config)
```
# app.ini deployed using UWSGI
[uwsgi]
home = /var/www/cargobase/venv
webapps = /var/www/cargobase/
app = %(webapps)
log-reopen = true

chdir = %(app)/
pidfile = %(webapps)/cargobase_worker.pid

mount = /=worker:app
callable = app

manage-script-name = true
socket = /tmp/cargobase.sock
master = true
processes = 4
threads = 4
thread-stacksize = 512

reload-on-rss = 60

harakiri = 500
vacuum = True
buffer-size=32768
limit-post = 51200000
post-buffering = 1
```

## worker.ini (flask RQ worker)
```
# flask worker.ini deployed using UWSGI
[uwsgi]
home = /var/www/cargobase/venv
webapps = /var/www/cargobase/
app = %(webapps)
log-reopen = true

chdir = %(app)/
pidfile = %(webapps)/cargobase_worker.pid

mount = /=worker:app
callable = app

manage-script-name = true
socket = /tmp/cargobase_worker.sock
master = true
processes = 4
threads = 4
thread-stacksize = 512

reload-on-rss = 60

harakiri = 500
vacuum = True
buffer-size=32768
limit-post = 51200000
post-buffering = 1
```


## Author
* **Budiyono Salim** - *Initial work* - [Budiyono Salim](https://github.com/bsalim)
