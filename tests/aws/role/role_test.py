import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam, mock_sts

from pacu.aws.role import create, delete

from tests.lib import aws_credentials, iam, sts


if TYPE_CHECKING:
    from mypy_boto3_iam import ServiceResource, service_resource


@pytest.fixture(scope='function')
def _role(iam, sts):
    create.main('test_role')
    _test_role = iam.Role('test_role')
    _test_role.load()

    yield _test_role


def test_role(_role):
    assert _role.name == 'test_role'


def test_delete(iam: 'ServiceResource', _role):
    delete.main(_role.name)

    with pytest.raises(iam.meta.client.exceptions.NoSuchEntityException):
        iam.User(_role.name).load()