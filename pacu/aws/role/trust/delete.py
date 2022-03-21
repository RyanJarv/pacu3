import json
import typing

import typer

import boto3
import botocore.errorfactory

app = typer.Typer()

# Allows for type completion of boto3 in some editors. There is no need for to get imported during runtime though.
if typing.TYPE_CHECKING:
    import mypy_boto3_iam


def main(name: str, arn: str):
    raise NotImplemented