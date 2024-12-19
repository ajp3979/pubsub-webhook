import flask
import pytest
from unittest import mock
from google.cloud import pubsub_v1

import main


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv('GCP_PROJECT', 'my-google-cloud-project')
    monkeypatch.setenv('TOPIC_NAME', 'my-topic')
    monkeypatch.delenv('TOPIC_PROJECT', raising=False)
    monkeypatch.setenv('IP_WHITELIST', '1.2.3.0/32')

@pytest.fixture
def data():
    data = '{"foo": "bar"}'
    bytes_representation = data.encode(encoding="utf-8")
    return bytes_representation



@pytest.fixture
def req(data):
    req = mock.MagicMock(spec=flask.Request)
    req.method = 'POST'
    req.remote_addr = '1.2.3.0'
    req.get_data = mock.MagicMock(return_value=data)

    return req


@pytest.fixture
def client(mocker):  # Use 'mocker' here
    mock_client = mocker.MagicMock(pubsub_v1.publisher.client.Client)
    mocker.patch('main.pubsub.PublisherClient', return_value=mock_client)

    return mock_client


def test_wrong_method(req):
    req.method = 'GET'

    assert main.pubsub_webhook(req) == ('Method not allowed', 405)


def test_allowed(req, env_vars):
    req.remote_addr = '1.2.3.0'

    assert main.pubsub_webhook(req) == 'OK'


def test_client(req, client, env_vars, data): # Uncommented and fixed
    assert main.pubsub_webhook(req) == 'OK'

    client.publish.assert_called_once_with(
            'projects/my-google-cloud-project/topics/my-topic',
            data)


def test_topic_project(req, client, env_vars, monkeypatch, data): # Add monkeypatch fixture
    monkeypatch.setenv('TOPIC_PROJECT', 'my-topic-project') # Use monkeypatch.setenv

    assert main.pubsub_webhook(req) == 'OK'

    client.publish.assert_called_once_with(
            'projects/my-topic-project/topics/my-topic',
            data)


def test_no_whitelist(req, client, monkeypatch, data):  # Corrected: use monkeypatch
    monkeypatch.setenv('GCP_PROJECT', 'my-google-cloud-project')
    monkeypatch.setenv('TOPIC_NAME', 'my-topic')
    monkeypatch.delenv('IP_WHITELIST', raising=False)  # Use monkeypatch.delenv
    assert main.pubsub_webhook(req) == 'OK'

    client.publish.assert_called_once_with(
            'projects/my-google-cloud-project/topics/my-topic',
            data)


def test_empty_data(req, client, env_vars):
    req.get_data.return_value = b''
    assert main.pubsub_webhook(req) == 'OK'

    client.publish.assert_called_once_with(
            'projects/my-google-cloud-project/topics/my-topic',
            b'')


