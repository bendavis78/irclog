#!/usr/bin/env python
import sys
import os
import glob
import re
from datetime import datetime
from flask import Flask, Response, render_template

app = Flask(__name__)


DEBUG = True
LOG_DIR = sys.argv[1]
SERVER = sys.argv[2]
CHAN = sys.argv[3]
PUBLIC = len(sys.argv) > 4 and sys.argv[4] == '--public'

app.config.from_object(__name__)

@app.route('/robots.txt')
def robots():
    if not app.config.get('PUBLIC', False):
        response = 'User-agent: *\nDisallow: /'
    else:
        response = ''

    return Response(response, mimetype='text/plain')

@app.route('/')
def index():
    # load today's log
    today = datetime.today()
    today_file = '{0}/{3:%Y}/{1}/{2}.{3:%m-%d}.log'.format(LOG_DIR, SERVER, CHAN, today)
    today_chat = open(today_file)
    years = os.listdir(LOG_DIR)
    context = {
        'server': SERVER,
        'chan': CHAN,
        'day': today,
        'years': sorted(years),
        'log': today_chat
    }
    return render_template('index.html', **context)

@app.route('/<y>/')
def year(y):
    dir = os.path.join(LOG_DIR, y, SERVER)
    logs = glob.glob('{}/{}*.log'.format(dir, CHAN))
    months = []
    for log in logs:
        match = re.match(r'^.+\.(\d+)-(\d+)\.log$', log)
        months.append(match.groups(0)[0])
    
    context = {
        'server': SERVER,
        'chan': CHAN,
        'year': y,
        'months': sorted(set(months)) 
    }
    return render_template('year.html', **context)

@app.route('/<y>/<m>/')
def month(y, m):
    dir = os.path.join(LOG_DIR, y, SERVER)
    logs = glob.glob('{}/{}.{}-*.log'.format(dir, CHAN, m))
    days = [re.match('^.+\.\d+-(\d+)\.log', l).groups(0)[0] for l in logs]
    context = {
        'server': SERVER,
        'chan': CHAN,
        'year': y,
        'month': m,
        'days': sorted(set(days))
    }
    return render_template('month.html', **context)

@app.route('/<y>/<m>/<d>/')
def day(y, m, d):
    dir = os.path.join(LOG_DIR, y, SERVER)
    logfile = '{}/{}.{}-{}.log'.format(dir, CHAN, m, d)
    context = {
        'server': SERVER,
        'chan': CHAN,
        'day': datetime(int(y),int(m),int(d)),
        'log': open(logfile)
    }
    return render_template('day.html', **context)

if __name__ == "__main__":
    app.run()
