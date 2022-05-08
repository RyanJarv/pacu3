# This code was heavily inspired by NCC Group's aws-inventory which is apache-2 licensed.
# TODO: figure out what's needed to accommodate that license
import dataclasses
import functools
import json
import re
from functools import partial
from queue import Queue
from threading import Thread
from typing import Any, Callable, List, Optional, Tuple

import botocore
import botocore.session
import botocore.config
import botocore.exceptions
import typer
from rich import print
from rich.columns import Columns
from botocore.client import BaseClient
from botocore.model import OperationModel

import pacu.config
from pacu.aws.lib.boto import get_model, get_models, make_api_call
from pacu.lib.utils import get_data_dir


def svc_worker(q):
    while True:
        work = q.get()

        try:
            if not work:
                break

            py_op = botocore.xform_name(work.op)
            print('[DEBUG] [%s][%s] Invoking API "%s". Python name "%s".' % (work.region, work.svc, work.op, py_op))

            try:
                response = make_api_call(py_op, work.client)
            except botocore.exceptions.ClientError as e:
                print(f'[ERROR] failed to retrieve results for {work.op}:{py_op}. Skipping...')
                continue
            except Exception as e:  # TODO: remove catch all
                print(f'[ERROR] failed to retrieve results for {work.op}:{py_op}. Skipping...')
                continue

            work.store.add_response(work.svc, work.region, work.op, response)
        # except Exception as e:
        # work.store.add_exception(work.svc, work.region, work.op, e)
        # print('[FATAL] Unknown error while invoking API for service "%s" in region "%s". -- %s' % (work.svc, work.region, e.args))
        finally:
            q.task_done()


class ResultStore(object):
    def __init__(self, profile):
        self.profile = profile

    def add_response(self, service, region, svc_op, resp):
        p = get_data_dir() / 'aws' / self.profile / 'responses' / str(region) / service / svc_op
        p.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
        p.write_text(json.dumps(resp, default=str))

    def add_exception(self, service, region, svc_op, exc):
        p = get_data_dir() / 'aws' / self.profile / 'exceptions' / str(region) / service / svc_op
        p.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
        p.write_text(json.dumps(exc, default=str))


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


def main(services: List[str] = typer.Argument(None)):
    ingest('me', services)


def ingest(profile, services):
    sess = botocore.session.Session(profile=profile)
    if services:
        svcs = {}

        for service in services:
            if service not in sess.get_available_services():
                print(f'The specified service "{service}" is not valid. Below is a list of valid services:')
                print(Columns(sess.get_available_services()))
                exit(1)
            svcs[service] = get_model(service)
    else:
        svcs = get_models()

    store = ResultStore(profile)

    q, wait = start_threads(1, queue_maxsize=100)

    for svc_name, svc in svcs.items():
        config = botocore.config.Config()
        api_ver = sess.get_config_variable('api_versions').get(svc_name, None)
        regions = ['us-east-1']

        # svc_data = sess.get_service_data(svc_name, api_ver)
        # if svc_data['metadata'].get('globalEndpoint'):
        #     pass  # no regions will be return anything if it's a global endpoint
        # elif regions[0] not in sess.get_available_regions(svc_name):
        #     # import pdb; pdb.set_trace()
        #     continue

        ## TODO: why isn't this working?
        if svc_name in ['macie', 'mediastore-data']:
            continue

        for region in regions:
            try:
                client = sess.create_client(svc_name, region_name=region, api_version=api_ver, config=config)
            except botocore.exceptions.NoRegionError:
                print('[ERROR] [%s][%s] Issue in region detection. Skipping...' % ('us-east-1', svc_name))
                continue  # TODO: what should happen here?

            for op in filter(partial(allowed, svc_name), svc.operation_names):
                q.put(Work(svc=svc_name, op=op, region=region, client=client, store=store))