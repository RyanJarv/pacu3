#!/usr/bin/env python3
import re
import typer
import typing

from enum import Enum

import boto3

from botocore.exceptions import ClientError
from typer import colors, echo
from typing import Optional

from pacu.aws.lib import creds

app = typer.Typer()

# Allows for type completion of boto3 in some editors. There is no need for to get imported
# during runtime though.
if typing.TYPE_CHECKING:
    from mypy_boto3_sdb import Client


class HoneyTokenResult(Enum):
    Unknown = 1
    IsHoneyToken = 2
    Safe = 3


@app.command()
def add(name: str, access_key: str, secret_key: str, session_token: str = typer.Argument(None)):
    # TODO: Add these keys to the keystore (when we figure out what that should be)
    creds.add(name, access_key, secret_key, session_token)
    typer.echo("Added", color=colors.GREEN)

    # if cred.honey_token_check() == HoneyTokenResult.IsHoneyToken:
    #     typer.echo("Is honeytoken!", color=colors.RED)


@app.command()
def list():
    for cred in creds.list():
        print(f"{cred.Id}: {cred.AccessKey}")


@app.command()
def use(name: str):
    creds.use(name)


@app.command()
def honey_token_check(access_key_id: str, secret_access_key: str, session_token: Optional[str]) -> HoneyTokenResult:
    sess = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
    )
    client = sess.client('sdb')
    print('Making test API request...\n')

    try:
        ret = client.list_domains()
        print(ret)
        return HoneyTokenResult.Unknown
    except ClientError as error:
        if error.response['Error']['Code'] == 'AuthorizationFailure':
            msg = error.response['Error']['Message']

            if re.match(r'.*(canarytokens.com|canarytokens.org).*', msg):
                echo(
                    'WARNING: Keys are confirmed honey token keys from Canarytokens.org! Do not use them!',
                    color=colors.RED,
                )
                return HoneyTokenResult.IsHoneyToken
            elif re.match(r'.*(arn:aws:iam::534261010715:|arn:aws:sts::534261010715:).*', msg):
                echo(
                    'WARNING: Keys belong to an AWS account owned by Canarytokens.org! Do not use them!',
                    color=colors.RED,
                )
                return HoneyTokenResult.IsHoneyToken
            elif re.match(r'.*arn:aws:iam::.*', msg) and re.match(r'.*/SpaceCrab/.*', msg):
                echo(
                    'WARNING: Keys are confirmed honey token keys from SpaceCrab! Do not use them!',
                    color=colors.RED,
                )
                return HoneyTokenResult.IsHoneyToken
        else:
            raise UserWarning('Did not receive AuthorizationFailure sdb:ListDomains, should this happen?')

        echo('Keys appear to be real (not a honey token key)!', color=colors.RED)
        return HoneyTokenResult.Safe