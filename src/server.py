from flask import Flask
from flask import Response

import requests

app = Flask(__name__)

login = ''
password = ''
credentials=(login, password)
api='https://evojam.atlassian.net/rest/api/latest'
timesheets_api='https://evojam.atlassian.net/rest/tempo-timesheets/3'

@app.route("/api")
def hello():
    return "Hello World!"

@app.route("/health")
def health():
    return Response("{'Status':'working'}", status=200, mimetype='application/json')

@app.route("/test")
def test():
    response = requests.get(
        api + '/issue/EIP-78', 
        auth=(login, password)
    )
    return response.text, response.status_code

@app.route("/worklogs")
def worklogs():
    response = requests.get(
        timesheets_api + '/worklogs/',
        auth=credentials
    )
    return response.text, response.status_code