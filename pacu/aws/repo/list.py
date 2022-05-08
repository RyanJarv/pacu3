import functools
from pathlib import Path
from typing import Optional

import botocore.session
import typer
from botocore.model import OperationModel

from pacu.lib.utils import get_data_dir


def get_data_files(cloud=None, profile=None, region=None, svc=None):
    p = get_data_dir()

    glob = Path('')
    if cloud:
        glob = glob / cloud

    if profile:
        glob = glob / profile

    if region:
        glob = glob / region

    if svc:
        glob = glob / svc

    for node in p.rglob(str(glob/'**'/'*')):
        if node.is_file():
            yield node.relative_to(p)
        else:
            continue

@functools.cache
def op_model(svc, op) -> OperationModel:
    sess = botocore.session.get_session()
    ver = sess.get_config_variable('api_versions').get(svc, None)
    model = sess.get_service_model(svc, api_version=ver)
    return model.operation_model(op)


def main(
        profile: Optional[str] = typer.Argument(None),
        region: Optional[str] = typer.Argument(None),
        svc: Optional[str] = typer.Argument(None),
):
    list_resources(profile, region, svc)


def list_resources(profile=None, region=None, svc=None):
    for f in get_data_files(cloud='aws', profile=profile, region=region, svc=svc):
        cloud, profile, _, region, svc, call = f.parts
        print(f"{cloud} {profile} {region} {svc} {call}")