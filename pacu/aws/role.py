import json
import typing

import typer

import boto3
import botocore.errorfactory

app = typer.Typer()

from policyuniverse.policy import Policy

# Allows for type completion of boto3 in some editors. There is no need for to get imported
# during runtime though.
if typing.TYPE_CHECKING:
    import mypy_boto3_iam
    import mypy_boto3_sts


# TODO: Improve aws.role.create
#   * Don't make sts call if possible
#   * Figure out how to handle the trust_policy.
@app.command()
def create(name: str = typer.Argument(default=False)):
    """create will create a new IAM user with administrative permissions."""
    iam = boto3.resource('iam')

    sts = boto3.client('sts')
    arn = sts.get_caller_identity()['Arn']

    trust_policy = Policy(dict(
        Version='2010-08-14',
        Statement=[
            dict(
                Effect='Allow',
                Principal=arn,
                Action=['sts:AssumeRole'],
            ),
    ]))

    try:
        role = iam.create_role(RoleName=name, AssumeRolePolicyDocument=json.dumps(trust_policy.policy))
    except botocore.errorfactory.ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"[ERROR] The user {name} already exists.")
            return
        else:
            raise e



    role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')
    # TODO: add trust


@app.command()
def delete(name: str = typer.Argument(default=False)):
    """delete will delete the given user."""
    iam = boto3.resource('iam')
    role = iam.Role(name)

    for policy in role.attached_policies.all():
        policy.detach_role(RoleName=role.name)

    role.delete()
    print(f"User {name} successfully deleted.")


@app.command()
def list():
    raise NotImplemented


def _list():
    raise NotImplemented