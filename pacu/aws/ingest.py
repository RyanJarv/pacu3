# TODO: copied from aws-inventory for testing
import dataclasses
import functools
import json
import re
from datetime import datetime
from functools import partial
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Any, Callable, Dict, Optional, Tuple

import botocore
import botocore.session
import botocore.config
import botocore.exceptions
import typer
from botocore.client import BaseClient
from botocore.model import OperationModel, ServiceModel

import pacu.config
from pacu.lib.utils import get_data_dir


def get_models() -> Dict[str, ServiceModel]:
    sess = botocore.session.get_session()

    model = {}
    for svc_name in sess.get_available_services():
        api_version = sess.get_config_variable('api_versions').get(svc_name, None)
        model[svc_name] = sess.get_service_model(svc_name, api_version=api_version)

    return model


def make_api_call(py_op, work):
    if work.client.can_paginate(py_op):
        paginator = work.client.get_paginator(py_op)
        response = paginator.paginate().build_full_result()
    else:
        response = getattr(work.client, py_op)()
    return response


def svc_worker(q):
    while True:
        work = q.get()

        try:
            if not work:
                break

            py_op = botocore.xform_name(work.op)
            print('[DEBUG] [%s][%s] Invoking API "%s". Python name "%s".' % (work.region, work.svc, work.op, py_op))

            try:
                response = make_api_call(py_op, work)
            except botocore.exceptions.ClientError as e:
                print(f'[ERROR] failed to retrieve results for {work.op}:{py_op}. Skipping...')
                continue

            work.store.add_response(work.svc, work.region, work.op, response)
        except Exception as e:
            work.store.add_exception(work.svc, work.region, work.op, e)
            print('[FATAL] Unknown error while invoking API for service "%s" in region "%s".' % (work.svc, work.region))
        finally:
            q.task_done()


class ResultStore(object):
    def __init__(self, graph):
        self.profile = graph

    def add_response(self, service, region, svc_op, resp):
        try:
            p = get_data_dir() / self.profile / 'aws' / 'responses' / str(region) / service / svc_op
            p.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
            p.write_text(json.dumps(resp, default=str))
        except Exception as e:
            import pdb; pdb.set_trace()
            pass

    def add_exception(self, service, region, svc_op, exc):
        try:
            p = get_data_dir() / self.profile / 'aws' / 'exceptions' / str(region) / service / svc_op
            p.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
            p.write_text(json.dumps(exc, default=str))
        except Exception as e:
            import pdb; pdb.set_trace()
            pass


def start_threads(num, queue_maxsize) -> 'Tuple[Queue[Optional[Work]], Callable[[], Any]]':
    threads = []
    q: Queue[Optional[Work]] = Queue(maxsize=queue_maxsize)

    for _ in range(num):
        worker = Thread(target=svc_worker, args=(q,))
        worker.daemon = True
        worker.start()
        threads.append(worker)

    def wait():
        for _ in range(num):
            q.put(None)

        q.join()
    return q, wait


@dataclasses.dataclass
class Work:
    svc: str
    op: str
    region: str
    client: BaseClient
    store: ResultStore


@functools.cache
def op_model(svc, op) -> OperationModel:
    sess = botocore.session.get_session()
    ver = sess.get_config_variable('api_versions').get(svc, None)
    model = sess.get_service_model(svc, api_version=ver)
    return model.operation_model(op)


def allowed(svc, op) -> bool:
    if op in pacu.config.blacklist.get(svc, []):
        return False

    if not re.match(r'^(Describe|List).+', op):
        return False

    input = op_model(svc, op).input_shape
    if not input or input.required_members:
        return False

    return True


def main():
    svcs = get_models()

    config = botocore.config.Config()
    sess = botocore.session.Session(profile='me')
    store = ResultStore('data')

    q, wait = start_threads(1, queue_maxsize=1)

    selected_regions = ['us-east-1']

    for svc_name, svc in svcs.items():
        api_ver = sess.get_config_variable('api_versions').get(svc_name, None)
        regions = sess.get_available_regions(svc_name)
        if not regions:
            regions = [None]  # type: ignore # TODO: what should this default to?

        for region in regions:
            if region not in selected_regions:
                continue

            try:
                client = sess.create_client(svc_name, region_name=region, api_version=api_ver, config=config)
            except botocore.exceptions.NoRegionError:
                print('[ERROR] [%s][%s] Issue in region detection. Skipping...' % ('us-east-1', svc_name))
                continue  # TODO: what should happen here?

            for op in filter(partial(allowed, svc_name), svc.operation_names):
                q.put(Work(svc=svc_name, op=op, region=region, client=client, store=store))

    wait()