import os
import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam

from . import user

if TYPE_CHECKING:
    from mypy_boto3_iam import ServiceResource, service_resource


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope='function')
def iam(aws_credentials):
    with mock_iam():
        yield boto3.resource('iam', region_name='us-east-1')


@pytest.fixture(scope='function')
def test_user(iam):
    user.create('test_user')
    _test_user = iam.User('test_user')
    _test_user.load()

    yield _test_user


def test_delete(iam: 'ServiceResource', test_user: 'service_resource.User'):
    user.delete(test_user.user_name)

    with pytest.raises(iam.meta.client.exceptions.NoSuchEntityException):
        iam.User(test_user.user_name).load()


def test_list(test_user: 'service_resource.User'):
    assert 'test_user' in user._list()


def test_add(test_user: 'service_resource.User'):
    raise NotImplemented


def test_add_creds(test_user: 'service_resource.User'):
    raise NotImplemented
