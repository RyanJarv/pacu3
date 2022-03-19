import os
import boto3
import pytest

from typing import TYPE_CHECKING
from moto import mock_ec2

from . import ec2

if TYPE_CHECKING:
    from mypy_boto3_ec2 import ServiceResource, service_resource


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope='function')
def svc(aws_credentials):
    with mock_ec2():
        yield boto3.resource('ec2', region_name='us-east-1')


def test_delete(svc: 'ServiceResource', test_instance: 'service_resource.Instance'):
    resp = ec2._delete(svc, ec2.get_name(test_instance))
    assert len(resp['TerminatingInstances']) == 1
    assert resp['TerminatingInstances'][0]['CurrentState']['Name'] == 'shutting-down'


def test_list(test_ec2: 'service_resource.Instance'):
    assert 'test_ec2' in ec2._list()


def test_add(test_ec2: 'service_resource.Instance'):
    raise NotImplemented


def test_get_name():
    raise NotImplemented


def test_modify_userdata(test_ec2: 'service_resource.Instance'):
    ec2._modify_userdata('test_ec2', 'new_user_data')


@pytest.fixture(scope='function')
def vpc(svc: 'ServiceResource') -> 'service_resource.Vpc':
    vpc = ec2._add_vpc(svc, list(svc.vpcs.all())[0])
    assert type(vpc) == ec2.Vpc
    return vpc


@pytest.fixture(scope='function')
def subnet(svc: 'ServiceResource') -> 'ec2.Subnet':
    subnet =  ec2._add_subnet(svc, next(iter(svc.subnets.all())))
    assert type(subnet) == ec2.Subnet
    return subnet


@pytest.fixture(scope='function')
def security_group(svc: 'ServiceResource') -> ec2.SecurityGroup:
    group = ec2._add_security_group(svc, next(iter(svc.security_groups.all())))
    assert type(group) == ec2.SecurityGroup
    return group


@pytest.fixture(scope='function')
def region(svc: 'ServiceResource'):
    region = ec2._add_region(svc, 'us-east-1')
    assert type(region) == ec2.Region
    return region


@pytest.fixture(scope='function')
def key_pair(svc: 'ServiceResource', region) -> ec2.KeyPair:
    key = svc.create_key_pair(KeyName='test_key_pair', KeyType='rsa')
    key_pair = ec2._add_key_pair(svc, key)
    assert type(key_pair) == ec2.KeyPair
    return key_pair


@pytest.fixture(scope='function')
def test_instance(
        svc: 'ServiceResource',
        subnet: ec2.Subnet,
        security_group: ec2.SecurityGroup,
        key_pair: ec2.KeyPair,
) -> 'service_resource.Instance':
    inst = ec2._create(svc, 'test_ec2', subnet, security_group, key_pair)
    inst.reload()

    name_tag = ec2.get_name(inst)
    assert name_tag == 'test_ec2'

    yield inst


def test_instance_1(test_instance: 'service_resource.Instance'):
    assert test_instance.instance_id != ""
