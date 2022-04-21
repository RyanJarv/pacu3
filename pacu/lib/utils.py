import threading

import networkx

from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role


def run_thread(*args, **kwargs):
    t = threading.Thread(target=args[0], args=(args[1:]), kwargs=kwargs)
    t.daemon = True
    t.start()
    return t


def has_assumed(graph: networkx.Graph, src: Role, dst_arn: str) -> bool:
    """Returns True if an edge exist between the src Role and a role with the arn dst_arn.

    TODO: Probably doesn't make sense to use roles as nodes, can't retrieve the node by
     ARN or use has_edge if we do that.
    """
    for neighbor in graph.neighbors(src):
        if neighbor.arn == dst_arn:
            return True

    return False
