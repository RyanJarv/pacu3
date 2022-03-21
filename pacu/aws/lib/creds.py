import dataclasses
import typing
from typing import Optional

import boto3
from pacu.resources import BaseResource, Resource


@dataclasses.dataclass(kw_only=True)
class ActiveCredential(BaseResource):
    Name: str = None


@dataclasses.dataclass(kw_only=True)
class AwsCredential(BaseResource):
    AccessKey: str = None
    SecretKey: str = None

    SessionToken: Optional[str] = None


def add(name: str, access_key: str, secret_key: str, session_token: str = None):
    cred = AwsCredential(Id=name, AccessKey=access_key, SecretKey=secret_key, SessionToken=session_token)

    with Resource.new(cred):
        pass

    return cred


def list() -> typing.Iterator[AwsCredential]:
    return Resource.list(AwsCredential)


def use(name: str):
    with Resource.new(ActiveCredential(Id='current_account', Name=name)) as r:
        pass


def boto3_resource(service_name: str):
    active = Resource.get(ActiveCredential(Id='current_account'))
    cred = Resource.get(AwsCredential(Id=active.Name))
    return boto3.resource(
        service_name,
        aws_access_key_id=cred.AccessKey,
        aws_secret_access_key=cred.SecretKey,
        aws_session_token=cred.SessionToken,
    )


def boto3_client(service_name: str):
    active = Resource.get(ActiveCredential(Id='current_account'))
    cred = Resource.get(AwsCredential(Id=active.Name))
    return boto3.client(
        service_name,
        aws_access_key_id=cred.AccessKey,
        aws_secret_access_key=cred.SecretKey,
        aws_session_token=cred.SessionToken,
    )
