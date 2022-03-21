import os

import boto3
import pytest
from moto import mock_iam, mock_sts


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
def sts(aws_credentials):
    with mock_sts():
        yield boto3.resource('iam', region_name='us-east-1')
