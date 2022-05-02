import functools
from typing import Dict, List

import botocore.session
from botocore.client import BaseClient
from botocore.model import ListShape, OperationModel, ServiceModel, Shape, StructureShape

# Do not use this for making api calls, it is solely for accessing resource definitions
# TODO: Prevent this from being used in a stupid way.
sess = botocore.session.get_session()


def services():
    return sess.get_available_services()


def get_models() -> Dict[str, ServiceModel]:
    return {name: get_model(name) for name in services()}


def output_shape(svc: str, op: str) -> StructureShape:
    return get_op_model(svc, op).output_shape


@functools.cache
def get_model(svc: str) -> ServiceModel:
    ver = sess.get_config_variable('api_versions').get(svc, None)
    return sess.get_service_model(svc, api_version=ver)


def get_op_model(svc: str, op: str) -> OperationModel:
    return get_model(svc).operation_model(op)

default_params = {
    "iam": {
        "list_policies": {"Scope": "Local"},
    },
}


def make_api_call(py_op: str, client: BaseClient):
    params = default_params.get(client.meta.service_model.service_name, {}).get(py_op, {})
    if client.can_paginate(py_op):
        paginator = client.get_paginator(py_op)
        response = paginator.paginate(**params).build_full_result()
    else:
        response = getattr(client, py_op)(**params)
    return response
