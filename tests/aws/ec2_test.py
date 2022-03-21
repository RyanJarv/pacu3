import base64
import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_ec2

from pacu.aws import ec2

from tests.lib import aws_credentials

if TYPE_CHECKING:
    from mypy_boto3_ec2 import ServiceResource, service_resource


@pytest.fixture(scope='function')
def svc(aws_credentials):
    with mock_ec2():
        yield boto3.resource('ec2', region_name='us-east-1')


def test_delete(svc: 'ServiceResource', test_instance: 'service_resource.Instance'):
    name = ec2.get_name(test_instance)
    assert name is not None
    resp = ec2._delete(svc, name)
    assert len(resp['TerminatingInstances']) == 1
    assert resp['TerminatingInstances'][0]['CurrentState']['Name'] == 'shutting-down'


@pytest.fixture(scope='function')
def test_instance(
        svc: 'ServiceResource',
) -> 'service_resource.Instance':
    inst = ec2._create(
        svc,
        'test_ec2',
        list(svc.subnets.all())[0].id,
        list(svc.security_groups.all())[0].id,
        svc.create_key_pair(KeyName='test_key_pair', KeyType='rsa').name,
    )
    inst.reload()

    name_tag = ec2.get_name(inst)
    assert name_tag == 'test_ec2'

    return inst


def test_instance_1(test_instance: 'service_resource.Instance'):
    assert test_instance.instance_id != ""


def test_modify_userdata(svc: 'ServiceResource', test_instance):
    ec2._modify_userdata(svc, ec2.get_name(test_instance), 'test_userdata')
    resp = test_instance.describe_attribute(Attribute='userData')
    user_data = resp['UserData']['Value']
    assert base64.b64decode(user_data).decode() == 'test_userdata'