import flask as flask
from flask import Flask
from flask import Response
from flask import request

import os
import requests
import json

from datetime import date, timedelta, datetime
from random import randint

app = Flask(__name__)

login = os.environ['JIRA_USER']
passw = os.environ['JIRA_PASS']
api = 'https://evojam.atlassian.net/rest/api/latest'
timesheets_api = 'https://evojam.atlassian.net/rest/tempo-timesheets/3'


def reversed_date(date):
    splitted = date.split('-')
    splitted.reverse()
    return '-'.join(splitted)


@app.route("/api")
def hello():
    return "Hello World!"


@app.route("/health")
def health():
    return Response("{'Status':'working'}", status=200, mimetype='application/json')


@app.route("/worklogs")
def worklogs():
    response = requests.get(
        timesheets_api + '/worklogs/',
        auth=credentials
    )
    return response.text, response.status_code


class Worklog:
    def __init__(self, name, minutes, date):
        self.name = name
        self.minutes = minutes
        self.date = date


def parse_worklog(record):
    name = record['author']['displayName']
    minutes = int(int(record['billedSeconds'])/60)
    date = reversed_date(record['dateCreated'][0:10])
    return Worklog(name, minutes, date)


@app.route("/api/dashboard")
def dashboard():
    date_from = reversed_date(request.args['from'])
    date_to = reversed_date(request.args['to'])

    url = timesheets_api + '/worklogs/?dateFrom=' + date_from + '&dateTo=' + date_to

    response = requests.get(url, auth=(login, passw))
    worklogs = [parse_worklog(record) for record in response.json()]

    names = list(set([w.name for w in worklogs]))
    
    d = dict([(name, list()) for name in names])

    start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    delta = end_date - start_date
    date_range = []

    for i in range(delta.days + 1):
        date_range.append(start_date + timedelta(days=i))

    for name in names:
        for day in date_range:
            d[name].append({'date': day.strftime('%d-%m-%Y'), 'minutes': 0, 'id': randint(0, 999999999)})

        # d[w.name].append({'date': w.date, 'minutes': w.minutes})  

    for w in worklogs:
        for item in d[w.name]:
            if w.date == item['date']:
                item['minutes'] = item['minutes'] + w.minutes

    result = list()

    for name, data in d.items():
        result.append({
            'name': name,
            'data': data,
	})

    return Response(json.dumps(result), 200, mimetype='application/json')

