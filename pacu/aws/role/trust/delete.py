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


@app.command()
def delete():
    pass