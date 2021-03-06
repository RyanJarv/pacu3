import threading
from pathlib import Path

import networkx
import typer

from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role


def run_thread(*args, **kwargs):
    t = threading.Thread(target=args[0], args=(args[1:]), kwargs=kwargs)
    t.daemon = True
    t.start()
    return t


def has_assumed(graph: networkx.Graph, src_arn: str, dst_arn: str) -> bool:
    """Returns True if an edge exist between the src Role and a role with the arn dst_arn."""
    return graph.has_edge(src_arn, dst_arn)


def get_data_dir():
    return Path(typer.get_app_dir('pacu')) / 'data'


def get_aws_data_dir():
    return get_data_dir() / 'aws' / 'responses'
