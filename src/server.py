from flask import Flask
from flask import Response
from flask import request

import os
import requests

app = Flask(__name__)

login = os.environ['JIRA_USER']
passw = os.environ['JIRA_PASS']
credentials=(login, passw)

api='https://evojam.atlassian.net/rest/api/latest'
timesheets_api='https://evojam.atlassian.net/rest/tempo-timesheets/3'

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

@app.route("/api/dashboard")
def dashboard():
    date_from, date_to = requests.args['from'], requests.args['to']
    return '', 200