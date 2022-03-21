import json
import typing

import typer

import boto3
import botocore.errorfactory

# Allows for type completion of boto3 in some editors. There is no need for to get imported
# during runtime though.
if typing.TYPE_CHECKING:
    import mypy_boto3_iam


def main(name: str = typer.Argument(default=False)):
    """delete will delete the given user."""
    iam = boto3.resource('iam')
    role = iam.Role(name)

    for policy in role.attached_policies.all():
        policy.detach_role(RoleName=role.name)

    role.delete()
    print(f"User {name} successfully deleted.")