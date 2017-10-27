#!/usr/bin/python

from auto_jira_lib import AutoJira
from flask_httpauth import HTTPBasicAuth
from flask import Flask, request

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route("/")
def hello():
    return "Hello World!"

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@auth.get_password
def get_password(username):
  if username == "jack":
    return "jack"
  return None

@app.route('/shutdown', methods=['POST'])
@auth.login_required
def shutdown():
  shutdown_server()
  return 'Server shutting down...'

@app.route('/testdata', methods=['POST'])
@auth.login_required
def testdata():
  data = request.get_json()
  print "data type is %s" % type(data)
  print "data is :%s" % data
  
  return "test"

@app.route('/issue/<issue_id>', methods=['GET'])
def get_issue(issue_id):
  return "issue ID is %s " % issue_id, 201





if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)
