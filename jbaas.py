#!/usr/bin/python

from auto_jira_lib import AutoJira
from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)
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
  
  jbs = AutoJira()
  r = jbs.get_issue_with_id(issue_id)
  r = r.json()# type is dictionary
  print "issue type is %s" % type(issue_id)
  print "result type is  %s" % type(r)
  return "issue is %s " % r, 200

@app.route('/users', methods=['POST'])
@auth.login_required
def add_users():
  print "flask name is %s" % app.name
  post = request.get_json()
  post_id = mongo.db.users.insert_one(post).inserted_id
  #return "test_collection is %s" % test_collection, 200
  return "post id is %s" % post_id

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)
