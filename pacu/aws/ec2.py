import typing
from enum import Enum

import typer

import boto3
import botocore.errorfactory
from boto3.resources.base import ServiceResource

from pacu.resources import Resource

app = typer.Typer()

from typing import Optional, TYPE_CHECKING

# Allows for type completion of boto3 in some editors. There is no need for to get imported
# during runtime though.
if TYPE_CHECKING:
    from mypy_boto3_ec2 import ServiceResource, service_resource


@app.command()
def create(name: str = typer.Argument(default=False)):
    svc = boto3.resource('ec2')
    print(_create(svc, name).id)


# TODO: Improve aws.ec2._create
#   * How should we determine parameters for create_instances?
#     * KeyName
#     * SecurityGroupIds
#     * SubnetId
#     * IamInstanceProfile
#   * What are sane defaults for:
#     * ImageId
#     * InstanceType
#     * Monitoring
#     * UserData
#     * EbsOptimized
#     * HibernationOptions
#   * Figure out how to handle the instance name.
#     * Should it even be tagged?
#     * Ensure their is no duplicates.
def _create(
        svc: ServiceResource,
        name: str,
        subnet: 'Subnet',
        security_group: 'SecurityGroup',
        key_pair: 'KeyPair',
) -> 'service_resource.Instance':

    with Resource("ec2.instance").create(name):
        """create will create a new IAM user with administrative permissions."""
        insts = svc.create_instances(
            # us-east-1	focal	20.04 LTS	amd64	hvm:ebs-ssd	20220308	ami-01896de1f162f0ab7	hvm
            ImageId='ami-01896de1f162f0ab7',
            InstanceType='t2.small',
            # KeyName='string',
            MaxCount=1,
            MinCount=1,
            Monitoring={'Enabled': False},
            SecurityGroupIds=[security_group.resource.id],
            KeyName=key_pair.resource.name,
            SubnetId=subnet.resource.id,
            # UserData='string',
            # IamInstanceProfile={
            #     'Arn': 'string',
            #     'Name': 'string',
            # },
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{
                    'Key': 'Name',
                    'Value': f"pacu-{name}",
                }],
            }],
            MetadataOptions={
                'HttpTokens': 'required',
                'HttpPutResponseHopLimit': 1,
                'HttpEndpoint': 'enabled',
                'HttpProtocolIpv6': 'disabled',
                'InstanceMetadataTags': 'enabled',
            },
        )

    if len(insts) != 1:
        raise UserWarning(f"create_instances returned {len(insts)} instances (expected 1)")

    return insts[0]


@app.command()
def delete(name: str = typer.Argument(default=False)):
    svc = boto3.resource('ec2')
    print(svc, _delete(svc, name))


def _delete(svc: ServiceResource, name: str = typer.Argument(default=False)):
    with Resource("ec2.instance").delete(name):
        inst = get_instance(svc, name)
        if inst is None:
            raise UserWarning(f'no instance with name {name}')

        return inst.terminate()


def get_name(inst: 'service_resource.Instance') -> Optional[str]:
    if inst.tags is None:
        return None

    name_tag = list(filter(lambda t: t['Key'] == 'Name', inst.tags))
    if len(name_tag) != 1:
        return None

    return name_tag[0]['Value'].removeprefix("pacu-")


def get_instance(svc: 'ServiceResource', name: str) -> Optional['service_resource.Instance']:
    insts = list(svc.instances.filter(Filters=[{
        "Name": "tag:Name",
        "Values": [f"pacu-{name}"],
    }]))

    if len(insts) != 1:
        return None

    return insts[0]


def _list():
    raise NotImplemented


def _modify_userdata(name, new_user_data):
    return None


class Vpc:
    def __init__(self, resource: 'service_resource.Vpc'):
        self.resource = resource


def _add_vpc(svc, resource: 'service_resource.Vpc') -> Vpc:
    return Vpc(resource)


class Subnet:
    def __init__(self, resource: 'service_resource.Subnet'):
        self.resource = resource


def _add_subnet(svc, resource: 'service_resource.Subnet') -> Subnet:
    return Subnet(resource)


class SecurityGroup:
    def __init__(self, resource: 'service_resource.SecurityGroup'):
        self.resource = resource


def _add_security_group(svc, resource: 'service_resource.SecurityGroup') -> SecurityGroup:
    return SecurityGroup(resource)


class Region:
    def __init__(self, resource: str):
        self.resource = resource


def _add_region(svc, region_name) -> Region:
    return Region(region_name)


class KeyPair:
    def __init__(self, resource: 'service_resource.KeyPair'):
        self.resource = resource


def _add_key_pair(svc, resource: 'service_resource.KeyPair') -> KeyPair:
    return KeyPair(resource)

#
# class ResourceState(Enum):
#     Added: str = 'Added'
#     Created: str = 'Created'
#
#
# class Resource:
#     def __init__(self, state):
#         pass