import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam, mock_sts

from pacu.aws.role import create, delete

from tests.lib import aws_credentials, iam, sts


if TYPE_CHECKING:
    from mypy_boto3_iam import ServiceResource, service_resource


@pytest.fixture(scope='function')
def role(iam, sts):
    create.main('test_role')
    _test_role = iam.Role('test_role')
    _test_role.load()

    yield _test_role


def test_role(role):
    assert role.name == 'test_role'


def test_delete(iam: 'ServiceResource', role):
    delete.main(role.name)

    with pytest.raises(iam.meta.client.exceptions.NoSuchEntityException):
        iam.User(role.name).load()