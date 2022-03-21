import dataclasses
from unittest import mock

import botocore.exceptions
import botocore.session
import pytest
from botocore.stub import Stubber
from tinydb import where

from pacu import config
from pacu.aws.creds import AwsCredential, _add, _list, honey_token_check, HoneyTokenResult
from tests.aws.lib.config_test import cred


def auth_error(msg: str):
    raise botocore.exceptions.ClientError(
        error_response={'Error': {'Code': 'AuthorizationFailure'}},
        operation_name='TestOpName',
    )


@mock.patch('boto3.Session.client')
def test_honey_token_unknown(client):
    assert honey_token_check('access_key', 'secret_key', 'session_token') == HoneyTokenResult.Unknown


@mock.patch('boto3.Session.client')
def test_canary_token_canarytokens_org(client):
    client.return_value = botocore.session.get_session().create_client('sdb')
    with Stubber(client.return_value) as stubber:
        stubber.add_client_error(
            'list_domains',
            service_error_code='AuthorizationFailure',
            service_message='... canarytokens.org ...',
        )
        assert honey_token_check('access_key', 'secret_key', 'session_token') == HoneyTokenResult.IsHoneyToken


@mock.patch('boto3.Session.client')
def test_canary_token_account_534261010715(client):
    client.return_value = botocore.session.get_session().create_client('sdb')
    with Stubber(client.return_value) as stubber:
        stubber.add_client_error(
            'list_domains',
            service_error_code='AuthorizationFailure',
            service_message='... arn:aws:sts::534261010715:...',
        )
        assert honey_token_check('access_key', 'secret_key', 'session_token') == HoneyTokenResult.IsHoneyToken


@mock.patch('boto3.Session.client')
def test_canary_token_space_crab(client):
    client.return_value = botocore.session.get_session().create_client('sdb')
    with Stubber(client.return_value) as stubber:
        stubber.add_client_error(
            'list_domains',
            service_error_code='AuthorizationFailure',
            service_message='... arn:aws:iam::  /SpaceCrab/...',
        )
        assert honey_token_check('access_key', 'secret_key', 'session_token') == HoneyTokenResult.IsHoneyToken