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

import hmac
from hashlib import sha1

import event_handler

import mock
import pytest


def get_secrets_fake(project_name, secret_name, version_num) -> bytes:
    return {"event-handler": b"foo", "event-handler-team1": b"foo-team1"}[secret_name]


@pytest.fixture
def client():
    event_handler.app.testing = True
    return event_handler.app.test_client()


def test_unauthorized_source(client):
    r = client.post("/", data="Hello")
    assert r.status_code == 403

    r = client.get("/", data="Hello")
    assert r.status_code == 403


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
def test_unverified_signature(client):
    r = client.post(
            "/",
            headers={
                "User-Agent": "GitHub-Hookshot",
                "X-Hub-Signature": "foobar",
            },
        )

    assert r.status_code == 403


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_verified_gitlab_signature(client):
    r = client.post(
        "/",
        data="Hello",
        headers={"X-Gitlab-Event": "test", "X-Gitlab-Token": "foo"},
    )
    assert r.status_code == 204

@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_verified_gitlab_signature_with_team(client):
    r = client.post(
        "/?team=team1",
        data="Hello",
        headers={"X-Gitlab-Event": "test", "X-Gitlab-Token": "foo-team1"},
    )
    assert r.status_code == 204


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_incorrect_gitlab_team(client):
    r = client.post(
        "/?team=unknown",
        data="Hello",
        headers={"X-Gitlab-Event": "test", "X-Gitlab-Token": "foo"},
    )
    assert r.status_code == 403


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_incorrect_gitlab_signature(client):
    r = client.post(
        "/",
        data="Hello",
        headers={"X-Gitlab-Event": "test", "X-Gitlab-Token": "bar"},
    )
    assert r.status_code == 403


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_incorrect_gitlab_signature_team(client):
    r = client.post(
        "/?team=team1",
        data="Hello",
        headers={"X-Gitlab-Event": "test", "X-Gitlab-Token": "foo"},
    )
    assert r.status_code == 403


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_verified_jira_signature(client):
    r = client.post(
        "/?token=foo",
        data="Hello",
        headers={"User-Agent": "Atlassian Webhook HTTP Client"},
    )
    assert r.status_code == 204


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_verified_jira_signature_team(client):
    r = client.post(
        "/?team=team1&token=foo-team1",
        data="Hello",
        headers={"User-Agent": "Atlassian Webhook HTTP Client"},
    )
    assert r.status_code == 204


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_incorrect_jira_signature(client):
    r = client.post(
        "/?token=bar",
        data="Hello",
        headers={"User-Agent": "Atlassian Webhook HTTP Client"},
    )
    assert r.status_code == 403


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_incorrect_jira_signature_team(client):
    r = client.post(
        "/?team=team1&token=foo",
        data="Hello",
        headers={"User-Agent": "Atlassian Webhook HTTP Client"},
    )
    assert r.status_code == 403


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
@mock.patch(
    "event_handler.publish_to_pubsub", mock.MagicMock(return_value=True)
)
def test_verified_signature(client):
    signature = "sha1=" + hmac.new(b"foo", b"Hello", sha1).hexdigest()
    r = client.post(
        "/",
        data="Hello",
        headers={"User-Agent": "GitHub-Hookshot", "X-Hub-Signature": signature},
    )
    assert r.status_code == 204


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
def test_data_sent_to_pubsub(client):
    signature = "sha1=" + hmac.new(b"foo", b"Hello", sha1).hexdigest()
    event_handler.publish_to_pubsub = mock.MagicMock(return_value=True)
    r = client.post("/", data="Hello", headers={
        "User-Agent": "GitHub-Hookshot",
        "Host": "localhost",
        "Content-Length": "5",
        "X-Hub-Signature": signature,
    })

    event_handler.publish_to_pubsub.assert_called_with(
        "github", b"Hello", {
            "User-Agent": "GitHub-Hookshot",
            "Host": "localhost",
            "Content-Length": "5",
            "X-Hub-Signature": signature,
            "X-Team": "default",
        }
    )
    assert r.status_code == 204


@mock.patch("sources.get_secret", mock.MagicMock(side_effect=get_secrets_fake))
def test_data_sent_to_pubsub_with_team(client):
    signature = "sha1=" + hmac.new(b"foo-team1", b"Hello", sha1).hexdigest()
    event_handler.publish_to_pubsub = mock.MagicMock(return_value=True)
    r = client.post("/?team=team1", data="Hello", headers={
        "User-Agent": "GitHub-Hookshot",
        "Host": "localhost",
        "Content-Length": "5",
        "X-Hub-Signature": signature,
    })
    assert r.status_code == 204

    event_handler.publish_to_pubsub.assert_called_with(
        "github", b"Hello", {
            "User-Agent": "GitHub-Hookshot",
            "Host": "localhost",
            "Content-Length": "5",
            "X-Hub-Signature": signature,
            "X-Team": "team1",
        }
    )
