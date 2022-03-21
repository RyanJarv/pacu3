from unittest import mock

import pytest
import boto3
from tinydb import where

from pacu.aws.lib import creds
from pacu import config


@pytest.fixture(scope='function')
def resources():
    config.resources().truncate()
    return config.resources()


@pytest.fixture(scope='function')
def cred(resources):
    yield creds.add(name='test_cred', access_key='access_key', secret_key='secret_key', session_token='session_token')


def test_add(cred):
    records = config.resources().search(
        (where('Type') == creds.AwsCredential.__name__)
        & (where('Id') == 'test_cred')
        & (where('AccessKey') == 'access_key')
        & (where('SecretKey') == 'secret_key')
        & (where('SessionToken') == 'session_token')
    )
    assert len(records) == 1
    assert records[0]['AccessKey'] == 'access_key'


def test_list(cred):
    _creds = list(creds.list())
    assert len(_creds) == 1
    assert _creds[0] == cred


@pytest.fixture(scope='function')
def active_creds(cred):
    yield creds.use(cred.Id)


def test_active_cred(active_creds):
    records = config.resources().search(
        (where('Type') == creds.ActiveCredential.__name__)
        & (where('Id') == 'current_account')
    )
    assert len(records) == 1


@mock.patch('boto3.resource')
def test_boto3_resource(resource, active_creds):
    creds.boto3_resource('ec2')
    resource.assert_called_with(
        'ec2',
        aws_access_key_id='access_key',
        aws_secret_access_key='secret_key',
        aws_session_token='session_token',
    )


@mock.patch('boto3.client')
def test_boto3_client(client, active_creds):
    creds.boto3_client('ec2')
    client.assert_called_with(
        'ec2',
        aws_access_key_id='access_key',
        aws_secret_access_key='secret_key',
        aws_session_token='session_token',
    )

