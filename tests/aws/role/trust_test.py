import json

import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam, mock_sts

from pacu.aws.role.trust import create, delete
from tests.aws.role.role_test import role
from tests.lib import aws_credentials, iam, sts

from tests.lib import aws_credentials
from policyuniverse.policy import Policy
from policyuniverse.statement import PrincipalTuple, Statement



if TYPE_CHECKING:
    from mypy_boto3_iam import ServiceResource, service_resource


@pytest.fixture(scope='function')
def modified_role(role):
    create.main(role.name, 'arn:aws:sts::123456789012:user/test')
    role.reload()

    principals = [s['Principal'] for s in role.assume_role_policy_document['Statement']]
    assert 'arn:aws:sts::123456789012:user/test' in list(principals)

    return role


def test_create(modified_role):
    pass


def test_delete(modified_role):
    delete.main(modified_role.name, 'arn:aws:sts::123456789012:user/test')
    role.reload()

    principals = [s['Principal'] for s in modified_role.assume_role_policy_document['Statement']]

    assert 'arn:aws:sts::123456789012:user/test' not in list(principals)
