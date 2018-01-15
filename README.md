# evo-track-be
Backend for Evojam time tracking tool.

## Stack
- python3
- flask

## Usage
You need to have python3 and pip3 available in your path

### Retting active Jiras
Edit list `jiras` defined in `server.py`. It should contain names of jiras to be used. Name for jira is prefix of a link in form `prefix.atlassian.net`.

E.g. to use evojam and swingdev Jira:
```python
jiras = [
    'swingdev',
    'evojam'
]
```

### Setting up credentials
For each Jira, setup environmental variables with credentials (by hand or by editing `run` script). 

For Jira named `myjira` you should set `JIRA_USER_MYJIRA` with user name and `JIRA_TOKEN_MYJIRA` with user token.

### Running
```bash
sh install
sh run
```

Backend will run on `localhost:5000`.