import os
import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam

from pacu.aws import user

from tests.lib import aws_credentials

if TYPE_CHECKING:
    from mypy_boto3_iam import ServiceResource, service_resource


@pytest.fixture(scope='function')
def iam(aws_credentials):
    with mock_iam():
        yield boto3.resource('iam', region_name='us-east-1')


@pytest.fixture(scope='function')
def _user(iam):
    user.create('test_user')
    _test_user = iam.User('test_user')
    _test_user.load()

    yield _test_user


def test_user(_user):
    assert _user.name == 'test_user'


def test_delete(iam: 'ServiceResource', _user):
    user.delete(_user.user_name)

    with pytest.raises(iam.meta.client.exceptions.NoSuchEntityException):
        iam.User(_user.user_name).load()