#!/usr/bin/env python3

import json
import os
from datetime import timedelta, datetime
from random import randint

import requests
from flask import Flask
from flask import Response
from flask import request

app = Flask(__name__)


def creds_from_env(jira_name):
    uppercase = jira_name.upper()
    user_key = 'JIRA_USER_' + uppercase
    token_key = 'JIRA_TOKEN_' + uppercase
    return os.environ[user_key], os.environ[token_key]


jiras = [
    # "evojam",
    "pkupidura",
    "swingdev"
]

jiras_with_creds = dict([(j, creds_from_env(j)) for j in jiras])


def reversed_date(date):
    splitted = date.split('-')
    splitted.reverse()
    return '-'.join(splitted)


class Worklog:
    def __init__(self, name, minutes, date, key, avatar, jira):
        self.name = name
        self.minutes = minutes
        self.date = date
        self.key = key
        self.avatar = avatar
        self.jira = jira


def parse_worklog(record, jira):
    name = record['author']['displayName']
    key = record['issue']['key']
    minutes = int(int(record['billedSeconds']) / 60)
    date = reversed_date(record['dateStarted'][0:10])
    avatar = record['author']['avatar']
    return Worklog(name, minutes, date, key, avatar, jira)


@app.route("/api/dashboard")
def dashboard():
    date_from = reversed_date(request.args['from'])
    date_to = reversed_date(request.args['to'])

    worklogs = list()

    for jira, credentials in jiras_with_creds.items():
        url = 'https://' + jira + '.atlassian.net/rest/tempo-timesheets/3' + \
              '/worklogs?dateFrom=' + date_from + '&dateTo=' + date_to

        response = requests.get(
            url,
            auth=credentials,
            headers={'Accept': 'application/json'}
        )

        ws = [parse_worklog(record, jira) for record in response.json()]
        worklogs.extend(ws)

    names = list(set([w.name for w in worklogs]))

    avatars = dict()

    for w in worklogs:
        if w.name not in avatars:
            avatars[w.name] = w.avatar

    d = dict([(name, list()) for name in names])

    start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    delta = end_date - start_date
    date_range = []

    for i in range(delta.days + 1):
        date_range.append(start_date + timedelta(days=i))

    for name in names:
        for day in date_range:
            d[name].append({
                'date': day.strftime('%d-%m-%Y'),
                'minutes': 0,
                'id': randint(0, 999999999),
                'issues': []
            })

    for w in worklogs:
        for item in d[w.name]:
            if w.date == item['date']:
                item['minutes'] = item['minutes'] + w.minutes
                item['issues'].append({'key': w.key, 'time': w.minutes, 'jira': w.jira})

    result = list()

    for name, data in d.items():
        result.append({
            'name': name,
            'avatar': avatars[name],
            'data': data,
        })

    return Response(json.dumps(result), 200, mimetype='application/json')


@app.route("/api")
def hello():
    return "Hello World!"


@app.route("/health")
def health():
    return Response("{'Status':'working'}", status=200, mimetype='application/json')
