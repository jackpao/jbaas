"""
Copyright (c) 2017 Nutanix Inc. All rights reserved.

Author: han.pao@nutanix.com

Description: Auto-jira ticket filing
"""
# pylint: disable=bare-except

import  os, tarfile ,requests
from requests.auth import HTTPBasicAuth
#from framework.lib.nulog import ERROR, INFO, WARN

class AutoJira(object):
  """ Auto Jira lib"""

  HOST = "https://jira.nutanix.com"
  AUTH = ("infra_jira_user", "infra_jira_user")

  def __init__(self, auth=None, test_class=None, log_dir=None):
    """Instance initiator

    Args:
      auth(tuple), login user and password
      kwargs(json): Bug detail

    """
    if not auth:
      self.auth = HTTPBasicAuth(self.AUTH[0], self.AUTH[1])

    if not test_class:
      self.log_dir = log_dir
    else:
      self.log_dir = test_class.log_dir

  def _api(self, uri):
    """Internal func to get full url

    Args:
      uri(str): api call

    Returns:
      (str): The full url

    """
    return self.HOST + uri


  def _payload_allowed_values(self, **kwargs):
    """
    Args:

    """
    #Get the metadata of fields
    project = kwargs["Project"]
    issue_type = kwargs["Issuetype"]
    url = self._api("/rest/api/2/issue/createmeta?projectKeys=%s&\
            issuetypeNames=%s&expand=projects.issuetypes.fields" \
            % (project, issue_type))
    r = requests.get(url, auth = self.auth).json()

    #Check if primary component is valid
    allow_primary_com = r["projects"][0]["issuetypes"][0]["fields"]\
            ["customfield_15160"]["allowedValues"]
    allow_primary_com = [value["value"] for value in allow_primary_com]
    if kwargs["Primary Component"] not in allow_primary_com:
      raise ValueError("%s not valid in Primary Component" \
            % kwargs["Primary Component"])

    #Check versions if valid
    allow_versions = r["projects"][0]["issuetypes"][0]["fields"]\
            ["versions"]["allowedValues"]
    allow_versions = [value["name"] for value in allow_versions]
    if not all(version in allow_versions for version in kwargs["Versions"]):
      raise ValueError("%s not valid in affected versions" \
            % kwargs["Versions"])

    #Check components if valid
    allow_com = r["projects"][0]["issuetypes"][0]["fields"]\
            ["components"]["allowedValues"]
    allow_com = [value["name"] for value in allow_com]
    if not all(com in allow_com for com in kwargs["Components"]):
      raise ValueError("%s not valid in affected versions" \
            % kwargs["Components"])

    #Check if priority is valid
    allow_priority = r["projects"][0]["issuetypes"][0]["fields"]\
            ["priority"]["allowedValues"]
    allow_priority = [value["name"] for value in allow_priority]
    if kwargs["Priority"] not in allow_priority:
      raise ValueError("%s not valid in Priority" \
            % kwargs["Priority"])

  def _payload(self, **kwargs):
    """Create the correct payload format for jira api

    Args:
      kwargs(dict): bug info


    Returns:
      payload(dict): payload
    """

    self._payload_allowed_values(**kwargs)

    versions = [{"name": ver} for ver in kwargs["Versions"]]

    if "Components" in kwargs:
      components = [{"name": com} for com in kwargs["Components"]]
    else:
      components = []

    payload = {
      "fields": {
         "project":
         {
            "key": kwargs["Project"]
         },
         "summary": kwargs["Summary"],
         "description": kwargs["Description"],
         "issuetype": {
            "name": kwargs["Issuetype"]
         },
         "components": components,
         "customfield_15160": {
         	"value": kwargs["Primary Component"]
         },
         "fixVersions": [{
         	"name": "Triage"
         }],
         "customfield_10011": [{
         	"value": kwargs["Impact"]
         }],
         "versions": versions,
         "priority":{
         	"name": kwargs["Priority"]
         }
      }
    }
    return payload

  def attach_log(self, issue_id, log_dir):
    """Attach log to bug

    """
    url = self._api("/rest/api/2/issue/%s/attachments" % issue_id)
    headers = {"X-Atlassian-Token": "nocheck"}

    #for _, _, fnames in os.walk(log_dir):
    #  log_files = [log_dir + "/" + fname for fname in fnames]
    #print "log_files is %s" % log_files
    #tar = tarfile.open(log_dir + "/logs.tar", "w")
   # for log in log_files:
   #   tar.add(log)
   # tar.close()

    tar = tarfile.open(log_dir + "/logs.tar", "w")
    tar.add(log_dir)
    tar.close()
    send_file = {'file': open((log_dir + "/logs.tar"), "rb")}

    return requests.post(url, headers = headers, files=send_file, auth = self.auth)

  def create_issue(self, **kwargs):
    """ Create issue

    Args:
      **kwargs (dict): bug detail

    Returns:
      REST api call response


    """
    url = self._api("/rest/api/2/issue/")

    payload = self._payload(**kwargs)

    print "payload is %s" % payload

    return requests.post(url, json = payload, auth = self.auth )


  def get_issue_with_id(self, issue_id):
    """Get issue with key id

    Args:
      issue_id (str): issue id eg. ENG-111, AUTO-123

    Reuturns:
      REST api call respone

    """
    url = self._api("/rest/api/2/issue/%s" % issue_id)
    return requests.get(url, auth = self.auth)

  def metadata_ENG(self):

    url = self._api("/rest/api/2/issue/createmeta?projectKeys=ENG&issuetypeNames=Bug&expand=projects.issuetypes.fields")
    return requests.get(url, auth = self.auth)


def main():
  #auth = ("infra_jira_user", "infra_jira_user")
  j = AutoJira(log_dir = "/home/nutanix")
  r = j.get_issue_with_id("AUTO-14141")
  print "Status code is %s " % r.status_code
  print "response json key is %s" % r.json()["key"]
  """
  payload = {
    "fields": {
       "project":
       {
          "key": "ENG"
       },
       "summary": "REST API jira test",
       "description": "Creating of an issue using project keys and issue type names using the REST API",
       "issuetype": {
          "name": "Bug"
       },
       "customfield_15160": {
       	"value": "Infrastructure"
       },
       "fixVersions": [{
       	"name": "Triage"
       }],
       "customfield_10011": [{
       	"value": "Internal Only No Customer Impact"
       }],
       "versions": [{
       	"name": "master"
       }],
       "priority":{
       	"name": "Trivial - P4"
       }
   }
  }
  """
  payload = {
       "Project":"ENG",
       "Summary": "REST API jira test",
       "Description": "Creating of an issue using project keys and issue type names using the REST API",
       "Issuetype": "Bug",
       "Components":[],
       "Primary Component": "Infrastructure",
       "FixVersions": "Triage",
       "Impact": "Internal Only No Customer Impact"
       ,
       "Versions": [ "5.0"
       ],
       "Priority": "Trivial - P4"
  }


  #r = j.create_issue(**payload)
  #j._payload(**payload)

  r = j.attach_log("ENG-114478", "/home/jpao/nutest/logs/20171019_151053/infrastructure/breakfix/test_auto_jira/HadesTest/test_single_ssd_repair/infra_collected_logs")
  print "tyep response is %s" % type(r)
  print "Status code is %s " % r.status_code
  print "Response is %s" % r.json()
  #print "resposne key  is %s" % r.json()["key"]

if __name__ == "__main__":
  main()

