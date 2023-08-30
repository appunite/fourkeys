# Copyright 2020 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json

import main
import shared

import mock
import pytest


@pytest.fixture
def client():
    main.app.testing = True
    return main.app.test_client()


def test_not_json(client):
    with pytest.raises(Exception) as e:
        client.post("/", data="foo")

    assert "Expecting JSON payload" in str(e.value)


def test_not_pubsub_message(client):
    with pytest.raises(Exception) as e:
        client.post(
            "/",
            data=json.dumps({"foo": "bar"}),
            headers={"Content-Type": "application/json"},
        )

    assert "Not a valid Pub/Sub Message" in str(e.value)


def test_missing_msg_attributes(client):
    with pytest.raises(Exception) as e:
        client.post(
            "/",
            data=json.dumps({"message": "bar"}),
            headers={"Content-Type": "application/json"},
        )

    assert "Missing pubsub attributes" in str(e.value)


@mock.patch("shared.create_unique_id", mock.MagicMock(return_value="01010101010011"))
def test_github_event_processed(client):
    headers = {"User-Agent": "Atlassian Webhook HTTP Client", "X-Team": "team1"}
    pubsub_msg = {
        "message": {
            "data": base64.b64encode(jira_issue_updated.encode("utf-8")).decode("utf-8"),
            "attributes": {"headers": json.dumps(headers)},
            "message_id": "foobar",
        },
    }

    github_event = {
        "event_type": "jira:issue_updated",
        "id": "krowa_id",
        "metadata": jira_issue_updated,
        "time_created": 1692878976,
        "signature": "01010101010011",
        "msg_id": "krowa_message_id",
        "source": "jira",
        "team": "team1",
    }

    shared.insert_row_into_bigquery = mock.MagicMock()

    r = client.post(
        "/",
        data=json.dumps(pubsub_msg),
        headers={"Content-Type": "application/json"},
    )

    shared.insert_row_into_bigquery.assert_called_with(github_event)
    assert r.status_code == 204


jira_issue_updated = """{
  "timestamp": 1692878976180,
  "webhookEvent": "jira:issue_updated",
  "issue_event_type_name": "issue_generic",
  "user": {
    "self": "https://loudius.atlassian.net/rest/api/2/user?accountId=5bffb88e470dea35d693200a",
    "accountId": "5bffb88e470dea35d693200a",
    "avatarUrls": {
      "48x48": "https://secure.gravatar.com/avatar/91626bd495101800e67c19ffbee2f7dc?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FJM-1.png",
      "24x24": "https://secure.gravatar.com/avatar/91626bd495101800e67c19ffbee2f7dc?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FJM-1.png",
      "16x16": "https://secure.gravatar.com/avatar/91626bd495101800e67c19ffbee2f7dc?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FJM-1.png",
      "32x32": "https://secure.gravatar.com/avatar/91626bd495101800e67c19ffbee2f7dc?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FJM-1.png"
    },
    "displayName": "Jacek Marchwicki",
    "active": true,
    "timeZone": "Europe/Warsaw",
    "accountType": "atlassian"
  },
  "issue": {
    "id": "10160",
    "self": "https://loudius.atlassian.net/rest/api/2/10160",
    "key": "LD-109",
    "fields": {
      "statuscategorychangedate": "2023-08-24T14:09:36.146+0200",
      "issuetype": {
        "self": "https://loudius.atlassian.net/rest/api/2/issuetype/10011",
        "id": "10011",
        "description": "Tasks track small, distinct pieces of work.",
        "iconUrl": "https://loudius.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10318?size=medium",
        "name": "Task",
        "subtask": false,
        "avatarId": 10318,
        "entityId": "2736b829-c0d7-425e-9021-277efd302bc5",
        "hierarchyLevel": 0
      },
      "parent": {
        "id": "10113",
        "key": "LD-62",
        "self": "https://loudius.atlassian.net/rest/api/2/issue/10113",
        "fields": {
          "summary": "BAU",
          "status": {
            "self": "https://loudius.atlassian.net/rest/api/2/status/10008",
            "description": "",
            "iconUrl": "https://loudius.atlassian.net/",
            "name": "To Do",
            "id": "10008",
            "statusCategory": {
              "self": "https://loudius.atlassian.net/rest/api/2/statuscategory/2",
              "id": 2,
              "key": "new",
              "colorName": "blue-gray",
              "name": "To Do"
            }
          },
          "priority": {
            "self": "https://loudius.atlassian.net/rest/api/2/priority/3",
            "iconUrl": "https://loudius.atlassian.net/images/icons/priorities/medium.svg",
            "name": "Medium",
            "id": "3"
          },
          "issuetype": {
            "self": "https://loudius.atlassian.net/rest/api/2/issuetype/10012",
            "id": "10012",
            "description": "Epics track collections of related bugs, stories, and tasks.",
            "iconUrl": "https://loudius.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10307?size=medium",
            "name": "Epic",
            "subtask": false,
            "avatarId": 10307,
            "entityId": "d95562d1-b344-4300-88b1-58fd40362bf6",
            "hierarchyLevel": 1
          }
        }
      },
      "timespent": null,
      "customfield_10030": null,
      "customfield_10031": null,
      "project": {
        "self": "https://loudius.atlassian.net/rest/api/2/project/10002",
        "id": "10002",
        "key": "LD",
        "name": "Loudius",
        "projectTypeKey": "software",
        "simplified": true,
        "avatarUrls": {
          "48x48": "https://loudius.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10421",
          "24x24": "https://loudius.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10421?size=small",
          "16x16": "https://loudius.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10421?size=xsmall",
          "32x32": "https://loudius.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10421?size=medium"
        }
      },
      "fixVersions": [],
      "aggregatetimespent": null,
      "customfield_10035": null,
      "resolution": null,
      "customfield_10036": null,
      "customfield_10027": null,
      "customfield_10028": null,
      "customfield_10029": null,
      "resolutiondate": null,
      "workratio": -1,
      "watches": {
        "self": "https://loudius.atlassian.net/rest/api/2/issue/LD-109/watchers",
        "watchCount": 1,
        "isWatching": false
      },
      "issuerestriction": {
        "issuerestrictions": {},
        "shouldDisplay": false
      },
      "lastViewed": "2023-07-11T09:54:02.392+0200",
      "created": "2023-06-02T13:23:10.896+0200",
      "customfield_10020": null,
      "customfield_10021": null,
      "customfield_10022": null,
      "priority": {
        "self": "https://loudius.atlassian.net/rest/api/2/priority/3",
        "iconUrl": "https://loudius.atlassian.net/images/icons/priorities/medium.svg",
        "name": "Medium",
        "id": "3"
      },
      "customfield_10023": null,
      "customfield_10024": null,
      "customfield_10025": null,
      "customfield_10026": null,
      "labels": [],
      "customfield_10016": null,
      "customfield_10017": null,
      "customfield_10018": {
        "hasEpicLinkFieldDependency": false,
        "showField": false,
        "nonEditableReason": {
          "reason": "PLUGIN_LICENSE_ERROR",
          "message": "The Parent Link is only available to Jira Premium users."
        }
      },
      "customfield_10019": "0|i000lf:",
      "timeestimate": null,
      "aggregatetimeoriginalestimate": null,
      "versions": [],
      "issuelinks": [],
      "assignee": {
        "self": "https://loudius.atlassian.net/rest/api/2/user?accountId=63be9ac5eac4f07e3f3bc286",
        "accountId": "63be9ac5eac4f07e3f3bc286",
        "avatarUrls": {
          "48x48": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "24x24": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "16x16": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "32x32": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png"
        },
        "displayName": "krzysztof.daniluk",
        "active": true,
        "timeZone": "Europe/Warsaw",
        "accountType": "atlassian"
      },
      "updated": "2023-08-24T14:09:36.146+0200",
      "status": {
        "self": "https://loudius.atlassian.net/rest/api/2/status/10009",
        "description": "",
        "iconUrl": "https://loudius.atlassian.net/",
        "name": "In Progress",
        "id": "10009",
        "statusCategory": {
          "self": "https://loudius.atlassian.net/rest/api/2/statuscategory/4",
          "id": 4,
          "key": "indeterminate",
          "colorName": "yellow",
          "name": "In Progress"
        }
      },
      "components": [],
      "timeoriginalestimate": null,
      "description": null,
      "customfield_10010": null,
      "customfield_10014": null,
      "timetracking": {},
      "customfield_10015": null,
      "customfield_10005": null,
      "customfield_10006": null,
      "security": null,
      "customfield_10007": null,
      "customfield_10008": null,
      "attachment": [],
      "aggregatetimeestimate": null,
      "customfield_10009": null,
      "summary": "Add showkase preview activity to the app since showkase library is used anyway.",
      "creator": {
        "self": "https://loudius.atlassian.net/rest/api/2/user?accountId=63be9ac5eac4f07e3f3bc286",
        "accountId": "63be9ac5eac4f07e3f3bc286",
        "avatarUrls": {
          "48x48": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "24x24": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "16x16": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "32x32": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png"
        },
        "displayName": "krzysztof.daniluk",
        "active": true,
        "timeZone": "Europe/Warsaw",
        "accountType": "atlassian"
      },
      "subtasks": [],
      "reporter": {
        "self": "https://loudius.atlassian.net/rest/api/2/user?accountId=63be9ac5eac4f07e3f3bc286",
        "accountId": "63be9ac5eac4f07e3f3bc286",
        "avatarUrls": {
          "48x48": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "24x24": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "16x16": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png",
          "32x32": "https://secure.gravatar.com/avatar/49399b4ffb696978919aefec83e60659?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FK-4.png"
        },
        "displayName": "krzysztof.daniluk",
        "active": true,
        "timeZone": "Europe/Warsaw",
        "accountType": "atlassian"
      },
      "aggregateprogress": {
        "progress": 0,
        "total": 0
      },
      "customfield_10001": null,
      "customfield_10002": null,
      "customfield_10003": null,
      "customfield_10004": null,
      "environment": null,
      "duedate": null,
      "progress": {
        "progress": 0,
        "total": 0
      },
      "votes": {
        "self": "https://loudius.atlassian.net/rest/api/2/issue/LD-109/votes",
        "votes": 0,
        "hasVoted": false
      }
    }
  },
  "changelog": {
    "id": "11302",
    "items": [
      {
        "field": "resolution",
        "fieldtype": "jira",
        "fieldId": "resolution",
        "from": "10000",
        "fromString": "Done",
        "to": null,
        "toString": null
      },
      {
        "field": "status",
        "fieldtype": "jira",
        "fieldId": "status",
        "from": "10010",
        "fromString": "Done",
        "to": "10009",
        "toString": "In Progress"
      }
    ]
  }
}"""