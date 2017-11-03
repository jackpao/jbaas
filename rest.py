#!/usr/bin/python

import requests


payload = {
       "Project":"ENG",
       "Summary": "Automation Test Failed",
       "Test case name": "test",
       "Issuetype": "Bug",
       "Primary Component": "Infrastructure",
       "FixVersions": "Triage",
       "Impact": "Internal Only No Customer Impact",
       "Priority": "Minor - P3"
}

#r = requests.post("http://10.1.134.91:5000/shutdown", data=payload, auth=("jack", "jack"))

r = requests.post("http://10.1.134.91:5000/testdata", json=payload, auth=("jack", "jack"))

print "status %s" % r.status_code

print "Response is %s" % r.text


r = requests.get("http://10.1.134.91:5000/issue/ENG-115691")

print "status %s" % r.status_code

#print "Response is %s type is %s " % (r.text, type(r.text))



payload = {
       "username": "jack",
       "password": "jack",
       "email": "han.pao@nutanix.com"
}

#r = requests.post("http://10.1.134.91:5000/shutdown", data=payload, auth=("jack", "jack"))

r = requests.post("http://10.1.134.91:5000/users", json=payload, auth=("jack", "jack"))

print "status %s" % r.status_code

print "Response is %s" % r.text


