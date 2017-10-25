#!/usr/bin/python

import requests


r = requests.post("http://10.1.134.91:5000/shutdown")

print "status %s" % r.status_code

print "text %s" % r.text
