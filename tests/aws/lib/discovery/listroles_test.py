import networkx
import pytest

from pacu.aws.lib.discovery.list_roles import ListRolesSearch
from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role


# This is not actually testing the API call which is a bit difficult because we are doing weird things with credential
# lookup.
def test_run():
    access_queue = Lq()
    discovered_queue = Lq()
    g = networkx.Graph()
    list_roles = ListRolesSearch(graph=g, discovered_queue=discovered_queue, access_queue=access_queue)
    list_roles.run()


@pytest.mark.skip(reason="need to figure out how to patch the API call here")
def test_run_todo():
    access_queue = Lq()
    discovered_queue = Lq()
    g = networkx.Graph()
    list_roles = ListRolesSearch(graph=g, discovered_queue=discovered_queue, access_queue=access_queue)
    access_queue.broadcast(Role(graph=g, arn="arn:aws:iam::123456789012:user/test"))
    list_roles.run()

