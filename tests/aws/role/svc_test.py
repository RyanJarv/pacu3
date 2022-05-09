import pytest
import networkx

from pacu.aws.lib.exploit.role_bruteforce import BruteforceRole
from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role
from pacu.aws.lib.role_svc import RoleSvc
from pacu.aws.role.svc import new_roles


# @pytest.mark.skip("will only work in my account")
def test_run():
    graph = networkx.Graph()
    discovered_queue = Lq()
    access_queue = Lq()

    discovered_queue.depends_on(access_queue)
    access_queue.depends_on(discovered_queue)

    for role in new_roles(graph, ['me']):
        access_queue.broadcast(role)

    svc = RoleSvc(
        graph=graph,
        plugins=[
            BruteforceRole(
                graph=graph,
                discovered_queue=discovered_queue,
                access_queue=access_queue,
            ),
        ],
    )

    discovered_queue.broadcast(Role(graph=graph, arn='arn:aws:iam::336983520827:role/test'))
    discovered_queue.broadcast(Role(graph=graph, arn='arn:aws:iam::336983520827:role/us-east-1_n74s7ZUSq_Manage-only'))

    svc.run()

