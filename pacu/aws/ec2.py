import typing
import typer
import boto3

from enum import Enum
from pacu.resources import Resource
from typing import Optional, TYPE_CHECKING

app = typer.Typer()

# Allows for type completion of boto3 in some editors. There is no need for to get imported
# during runtime though.
if TYPE_CHECKING:
    import mypy_boto3_ec2 as ec2_t


@app.command()
def create(
        name: str = typer.Argument(default=False),
        subnet: str = typer.Argument(default=False),
        security_group: str = typer.Argument(default=False),
        key_pair: str = typer.Argument(default=False),
):
    svc = boto3.resource('ec2')
    print(_create(svc, name, subnet, security_group, key_pair).id)


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
        svc: 'ec2_t.ServiceResource',
        name: str,
        subnet: str,
        security_group: str,
        key_pair: str,
) -> 'ec2_t.service_resource.Instance':

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
            SecurityGroupIds=[security_group],
            KeyName=key_pair,
            SubnetId=subnet,
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
def modify_userdata(name: str = typer.Argument(default=False)):
    raise NotImplemented


def _modify_userdata(svc: 'ec2_t.ServiceResource', name: str, userdata: str):
    inst = get_instance(svc, name)
    inst.modify_attribute(UserData={"Value": userdata.encode()})


@app.command()
def delete(name: str = typer.Argument(default=False)):
    svc = boto3.resource('ec2')
    print(svc, _delete(svc, name))


def _delete(svc: 'ec2_t.ServiceResource', name: str = typer.Argument(default=False)):
    with Resource("ec2.instance").delete(name):
        inst = get_instance(svc, name)
        if inst is None:
            raise UserWarning(f'no instance with name {name}')

        return inst.terminate()


def get_name(inst: 'ec2_t.service_resource.Instance') -> Optional[str]:
    if inst.tags is None:
        return None

    name_tag = list(filter(lambda t: t['Key'] == 'Name', inst.tags))
    if len(name_tag) != 1:
        return None

    return name_tag[0]['Value'].removeprefix("pacu-")


def get_instance(svc: 'ec2_t.ServiceResource', name: str) -> Optional['ec2_t.service_resource.Instance']:
    insts = list(svc.instances.filter(Filters=[{
        "Name": "tag:Name",
        "Values": [f"pacu-{name}"],
    }]))

    if len(insts) != 1:
        return None

    return insts[0]