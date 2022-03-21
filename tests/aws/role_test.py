import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam, mock_sts

from pacu.aws import role

from tests.lib import aws_credentials


if TYPE_CHECKING:
    from mypy_boto3_iam import ServiceResource, service_resource


@pytest.fixture(scope='function')
def iam(aws_credentials):
    with (mock_iam(), mock_sts()):
        yield boto3.resource('iam', region_name='us-east-1')


@pytest.fixture(scope='function')
def _role(iam):
    role.create('test_role')
    _test_role = iam.Role('test_role')
    _test_role.load()

    yield _test_role


def test_role(_role):
    assert _role.name == 'test_role'


def test_delete(iam: 'ServiceResource', _role):
    role.delete(_role.name)

    with pytest.raises(iam.meta.client.exceptions.NoSuchEntityException):
        iam.User(_role.name).load()