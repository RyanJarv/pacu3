import functools
import json
import os
from pathlib import Path
from typing import Optional

import botocore.session
import typer
from botocore.model import OperationModel

from pacu.lib.utils import get_data_dir


def get_data_files(cloud=None, region=None, svc=None):
    p = get_data_dir()

    glob = Path('')
    if cloud:
        glob = glob / cloud

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
        cloud: Optional[str] = typer.Argument(None),
        profile: Optional[str] = typer.Argument(None),
        region: Optional[str] = typer.Argument(None),
        svc: Optional[str] = typer.Argument(None),
):
    for f in get_data_files(cloud='aws'):
        cloud, region, svc, call = f.parts
        model = op_model(svc, call)

        pass
        if obj.get('ResponseMetadata'):
            del obj['ResponseMetadata']
        for k, v in obj.items():
            if not v:
                continue
            _t = type(v)
            if _t == list:
                print('list size: ' + str(len(v)))
            elif _t in [str, int, bool]:
                print(v)
            elif _t == dict:
                print(v.keys())
            else:
                import pdb; pdb.set_trace()
            # print(type(v))
            # print(f"{k}: {v}")
