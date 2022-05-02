# TODO: copied from aws-inventory for testing
import dataclasses
import functools
import json
import re
from datetime import datetime
from functools import partial
from queue import Queue
from threading import Thread
from typing import Any, Callable, List, Optional, OrderedDict, Tuple, Union, cast

import botocore
import botocore.session
import botocore.config
import botocore.exceptions
import tinydb
import typer
from rich import print
from rich.columns import Columns
from botocore.client import BaseClient
from botocore.model import ListShape, MapShape, OperationModel, Shape, StringShape, StructureShape

import pacu.config
from pacu.aws.lib.boto import get_model, get_models, make_api_call, output_shape


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
            #except botocore.exceptions.ClientError, Exception as e:  # TODO: remove catch all
            except Exception as e:  # TODO: remove catch all
                print(f'[ERROR] failed to retrieve results for {work.op}:{py_op}. Skipping...')
                continue

            work.store.add_response(work.svc, work.region, work.op, response)
        # except Exception as e:
        # work.store.add_exception(work.svc, work.region, work.op, e)
        # print('[FATAL] Unknown error while invoking API for service "%s" in region "%s". -- %s' % (work.svc, work.region, e.args))
        finally:
            q.task_done()


def clean(thing):
    return json.loads(json.dumps(thing, default=str))  # Remove python objects


# def items(db: tinydb.TinyDB, svc: str, op: str, resp: Union[dict, list], shape: Shape = None, parent: Optional[int] = None):
#     if parent is None:
#         shape = cast(StructureShape, output_shape(svc, op))
#         try:
#             parent = db.insert({'_svc': svc, '_op': op, '_name': shape.name, '_type': shape.type_name, '_parent': parent, '_doc': shape.documentation})
#         except Exception as e:
#             import pdb; pdb.set_trace()
#             pass
#         items(db, svc, op, resp, shape, parent)
#     elif shape.type_name == 'structure':
#         shape = cast(StructureShape, shape)
#         parent = db.insert({'_svc': svc, '_op': op, '_name': shape.name, '_type': shape.type_name, '_parent': parent, '_doc': shape.documentation})
#         for name, sub_shape in shape.members.items():
#             if resp.get(name):
#                 items(db, svc, op, resp[name], sub_shape, parent)
#     elif shape.type_name == "list":
#         shape = cast(ListShape, shape)
#         parent = db.insert({'_svc': svc, '_op': op, '_name': shape.name, '_type': shape.type_name, '_parent': parent, '_doc': shape.documentation})
#         for item in resp:
#             items(db, svc, op, item, shape.member, parent)
#     else:
#         db.insert({'_svc': svc, '_op': op, '_name': shape.name, '_type': shape.type_name, '_doc': shape.documentation, '_parent': parent, '_value': str(resp)})

def items(db: tinydb.TinyDB, svc: str, op: str, resp: Union[dict, list], shape: Shape = None):
    if not shape:
        shape = cast(StructureShape, output_shape(svc, op))

    if not shape.members:
        return

    for name, _shape in shape.members.items():
        if not resp.get(name):
            continue
        for (key, value, value_shape) in _items(resp[name], _shape):
            db.insert(clean({'_svc': svc, '_op': op, '_shape': value_shape, 'key': key, 'value': value}))

# def findId(resp: OrderedDict):
#     keys = list(resp.keys())
#     search = ['arn', 'name', 'id']
#     filter(lambda x: _findId(x, search))
#
# def _findId(key: str, _list):
#     key = key.lower()
#     for i, value in enumerate(_list):
#         value = value.lower()
#         if key in value:
#             return _list[i]

def _items(resp: Union[dict, list], shape: Shape):
    if shape.type_name == 'string':
        try:
            shape = cast(StringShape, shape)
        except Exception as e:
            print(e)
            return

        yield [resp], resp, shape.name
    elif shape.type_name == 'map':
        # if not ('token' in _shape.name.lower() or 'reserved for future use' in _shape.documentation.lower()):
        #     print(f'[WARN] Skipping {svc}:{op}:{shape.name} because it is a token or reserved for future use.')
        #     continue

        try:
            shape = cast(MapShape, shape)
        except Exception as e:
            print(e)
            return

        # TODO: consider seperate records for each key.
        for key, value in resp.items():
            yield key, value, shape.name
    elif shape.type_name == 'structure':
        shape = cast(StructureShape, shape)

        try:
            try:
                yield list(resp.values())[0:2], resp, shape.name
            except Exception as e:
                print(e)
                return
        except Exception as e:
            print(e)
            return
    elif shape.type_name == 'list':
        try:
            shape = cast(ListShape, shape)
        except Exception as e:
            print(e)
            return

        try:
            for value in resp:
                try:
                    yield from _items(value, shape.member)
                except Exception as e:
                    print(e)
                    continue
        except Exception as e:
            print(e)
            return
    elif shape.type_name == 'timestamp':
        shape = cast(Shape, shape)
        resp = cast(datetime, resp)
        yield [], resp.isoformat(), shape
    elif shape.type_name == 'integer':
        yield [], resp, shape
    else:
        print(shape.type_name)
        return


class ResultStore(object):
    def __init__(self, db: tinydb.TinyDB):
        self.db: tinydb.TinyDB = db

    def add_response(self, service, region, svc_op, resp):
        items(self.db, service, svc_op, resp)
        # self.graph.
        # p = get_data_dir() / self.profile / 'aws' / 'responses' / str(region) / service / svc_op
        # p.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
        # p.write_text(json.dumps(resp, default=str))

    def add_exception(self, service, region, svc_op, exc):
        pass
        # try:
        #     p = get_data_dir() / self.profile / 'aws' / 'exceptions' / str(region) / service / svc_op
        #     p.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
        #     p.write_text(json.dumps(exc, default=str))
        # except Exception as e:
        #     print(f'[EXCEPTION]: {" ".join(e.args)}')


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
    sess = botocore.session.Session(profile='me')

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

    # svcs['firehose'] = get_models()['firehose']
    # svcs['cloudwatch'] = get_models()['cloudwatch']
    # svcs = get_models()

    # g = networkx.Graph
    db = tinydb.TinyDB('/tmp/test.db')
    store = ResultStore(db)

    q, wait = start_threads(1, queue_maxsize=100)

    for svc_name, svc in svcs.items():
        config = botocore.config.Config()
        api_ver = sess.get_config_variable('api_versions').get(svc_name, None)
        regions = ['us-east-1']

        svc_data = sess.get_service_data(svc_name, api_ver)
        # if svc_data['metadata'].get('globalEndpoint'):
        #     pass  # no regions will be return anything if it's a global endpoint
        # elif regions[0] not in sess.get_available_regions(svc_name):
        #     # import pdb; pdb.set_trace()
        #     continue

        ## TODO: why isn't this working?
        if svc_name in ['macie', 'mediastore-data']:
            continue

        if not regions:
            regions = [None]  # type: ignore # TODO: what should this default to?

        for region in regions:
            try:
                client = sess.create_client(svc_name, region_name=region, api_version=api_ver, config=config)
            except botocore.exceptions.NoRegionError:
                print('[ERROR] [%s][%s] Issue in region detection. Skipping...' % ('us-east-1', svc_name))
                continue  # TODO: what should happen here?

            for op in filter(partial(allowed, svc_name), svc.operation_names):
                q.put(Work(svc=svc_name, op=op, region=region, client=client, store=store))

    wait()
