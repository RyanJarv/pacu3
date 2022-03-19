import os
import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam, mock_sts

from . import role

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
    with (mock_iam(), mock_sts()):
        yield boto3.resource('iam', region_name='us-east-1')


@pytest.fixture(scope='function')
def test_role(iam):
    role.create('test_role')
    _test_role = iam.Role('test_role')
    _test_role.load()

    yield _test_role


def test_delete(iam: 'ServiceResource', test_role: 'service_resource.Role'):
    role.delete(test_role.name)

    with pytest.raises(iam.meta.client.exceptions.NoSuchEntityException):
        iam.User(test_role.name).load()


def test_list(test_role: 'service_resource.User'):
    assert 'test_role' in role._list()


def test_add(test_role: 'service_resource.User'):
    raise NotImplemented


def test_add_creds(test_role: 'service_resource.User'):
    raise NotImplemented
