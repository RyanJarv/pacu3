import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_iam, mock_sts

from pacu.aws import role

from tests.lib import aws_credentials


if TYPE_CHECKING:
    from mypy_boto3_iam import ServiceResource, service_resource