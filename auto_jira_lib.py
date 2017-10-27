"""
Copyright (c) 2017 Nutanix Inc. All rights reserved.

Author: han.pao@nutanix.com

Description: Auto-jira ticket filing
"""
# pylint: disable=bare-except

import requests, tarfile
from requests.auth import HTTPBasicAuth

class AutoJira(object):
  """ Auto Jira lib"""

  HOST = "https://jira.nutanix.com"
  AUTH = ("infra_jira_user", "infra_jira_user")

  def __init__(self, test_class=None, auth=None):
    """Instance initiator

    Args:
      auth(tuple): login user and password
      test_class(class): Nutest test class

    """
    if not auth:
      self.auth = HTTPBasicAuth(self.AUTH[0], self.AUTH[1])
    else:
      self.auth = HTTPBasicAuth(auth[0], auth[1])
    
    if test_class:
      self.test_class = test_class

  def attach_log(self, issue_id):
    """Attach log to bug

    Args:
      issue_id(str): issue id eg. ENG-12345

    Returns:
      REST api call response

    """
#    url = self._api("/rest/api/2/issue/%s/attachments" % issue_id)
#    headers = {"X-Atlassian-Token": "nocheck"}
#    tar = tarfile.open(self.test_class.log_dir + "/logs.tar", "w")
#    tar.add(self.test_class.log_dir)
#    tar.close()
#    send_file = {'file': open((self.test_class.log_dir + "/logs.tar"), "rb")}

#    return requests.post(url, headers=headers, files=send_file, auth=self.auth)

  def create_issue(self, **kwargs):
    """ Create issue

    Args:
      **kwargs (dict): bug detail

    Returns:
      REST api call response

    """
    url = self._api("/rest/api/2/issue/")

    payload = self._payload(**kwargs)

    DEBUG("payload is %s" % payload)

    return requests.post(url, json=payload, auth=self.auth)


  def get_issue_with_id(self, issue_id):
    """Get issue with key id

    Args:
      issue_id (str): issue id eg. ENG-111, AUTO-123

    Returns:
      REST api call respone

    """
    url = self._api("/rest/api/2/issue/%s" % issue_id)
    return requests.get(url, auth=self.auth)

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
      **kwargs (dict): bug detail

    Raises:
      ValueError: if invlaid value in bug payload
    """
    #Get the metadata of fields
    project = kwargs["Project"]
    issue_type = kwargs["Issuetype"]
    url = self._api("/rest/api/2/issue/createmeta?projectKeys=%s&\
            issuetypeNames=%s&expand=projects.issuetypes.fields" \
            % (project, issue_type))
    response = requests.get(url, auth=self.auth).json()

    #Check if primary component is valid
    allow_primary_com = response["projects"][0]["issuetypes"][0]["fields"]\
            ["customfield_15160"]["allowedValues"]
    allow_primary_com = [value["value"] for value in allow_primary_com]
    if kwargs["Primary Component"] not in allow_primary_com:
      raise ValueError("%s not valid in Primary Component" \
            % kwargs["Primary Component"])

    #Check versions if valid
    allow_versions = response["projects"][0]["issuetypes"][0]["fields"]\
            ["versions"]["allowedValues"]
    allow_versions = [value["name"] for value in allow_versions]
    if not all(version in allow_versions for version in kwargs["Versions"]):
      raise ValueError("%s not valid in affected versions" \
            % kwargs["Versions"])

    #Check components if valid
    allow_com = response["projects"][0]["issuetypes"][0]["fields"]\
            ["components"]["allowedValues"]
    allow_com = [value["name"] for value in allow_com]
    if not all(com in allow_com for com in kwargs["Components"]):
      raise ValueError("%s not valid in affected versions" \
            % kwargs["Components"])

    #Check if priority is valid
    allow_priority = response["projects"][0]["issuetypes"][0]["fields"]\
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

    # nutest_test.log as description
    with open((self.test_class.log_dir + "/nutest_test.log"), "r") as myfile:
      description = myfile.read()

    payload = {
      "fields": {
        "project":
        {
          "key": kwargs["Project"]
        },
        "summary": kwargs["Summary"],
        "description": description,
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
        },
        "customfield_20084":{
          "value": "Not Applicable"
        },
        "customfield_18060":[
          kwargs["Test case name"]
        ]
      }
    }
    return payload
