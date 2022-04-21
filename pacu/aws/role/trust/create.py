import json
import typing

import typer
import boto3

from policyuniverse.statement import Statement

app = typer.Typer()

# Allows for type completion of boto3 in some editors. There is no need for to get imported during runtime though.
if typing.TYPE_CHECKING:
    import mypy_boto3_iam


def main(name: str, arn: str):
    iam = boto3.resource('iam')

    role = iam.Role(name)
    policy: dict = role.assume_role_policy_document  # type: ignore

    policy['Statement'].append(Statement(dict(
        Effect='Allow',
        Principal=arn,
        Action=['sts:AssumeRole'],
    )).statement)

    role.AssumeRolePolicy().update(PolicyDocument=json.dumps(policy))
    print()