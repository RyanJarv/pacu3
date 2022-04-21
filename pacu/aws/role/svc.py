from typing import Generator, List

import boto3
import networkx
import typer

from pacu.aws.lib.discovery.cloudtrail import CloudTrailRoleSearch
from pacu.aws.lib.exploit.role_bruteforce import BruteforceRole
from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role
from pacu.aws.lib.role_svc import RoleSvc

app = typer.Typer()


def new_roles(graph: networkx.Graph, arns: List[str]) -> Generator[Role, None, None]:
    for arn in arns:
        sess = boto3.Session(profile_name=arn)
        # TODO: can we do this without making an API call?
        arn = sess.client("sts").get_caller_identity()['Arn']

        yield Role(graph=graph, arn=arn, session=sess)


@app.command()
def run(profiles: List[str] = typer.Option(...), sqs_queue: str = typer.Option(None)):
    graph = networkx.Graph()
    discovered_queue = Lq()
    access_queue = Lq()

    for role in new_roles(graph, profiles):
        access_queue.broadcast(role)

    svc = RoleSvc(
        graph=graph,
        plugins=[
            CloudTrailRoleSearch(
                graph=graph,
                discovered_queue=discovered_queue,
                access_queue=access_queue,
            ),
            BruteforceRole(
                graph=graph,
                discovered_queue=discovered_queue,
                access_queue=access_queue,
            ),
        ],
    )

    svc.run()


@app.command()
def get_cred(arn: str):
    raise NotImplemented