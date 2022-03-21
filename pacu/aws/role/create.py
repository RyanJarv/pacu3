import json
import typing

import typer
import boto3
import botocore.errorfactory

from policyuniverse.policy import Policy

# Allows for type completion of boto3 in some editors. There is no need for to get imported
# during runtime though.
if typing.TYPE_CHECKING:
    import mypy_boto3_iam
    import mypy_boto3_sts


# TODO: Improve aws.role.create
#   * Don't make sts call if possible
#   * Figure out how to handle the trust_policy.
def main(name: str = typer.Argument(default=False)):
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