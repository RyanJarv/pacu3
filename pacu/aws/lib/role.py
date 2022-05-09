import enum
import typing

import botocore.session
import botocore.credentials
from botocore.exceptions import ClientError
from botocore.utils import ArnParser
from typing import Dict, Optional

import networkx as nx
from networkx.classes.filters import hide_edges

import boto3

from pacu.lib.graph.access import Access

if typing.TYPE_CHECKING:
    import mypy_boto3_sts


class RoleState(enum.Enum):
    ActiveState = 0
    RefreshingState = 1
    FailedState = 2


# Inherit graph item
class Role(Access):
    _arn: str
    name: str
    account: str
    path: str

    state: RoleState

    # ExternalId is a list of strings, each item in the list is treated as potentially necessary to assume the role.
    #
    # This mostly is because the trust policy may contain multiple statements. We could be smart about parsing
    # the policy to avoid this if we really wanted to but there may be times when we simply want to
    # try whatever we think might work.
    externalId: str

    creds: botocore.credentials.DeferredRefreshableCredentials
    sess: boto3.Session

    def __init__(self, graph: nx.Graph, arn: str, source_arn: str = None, session=None):
        self.arn = arn
        self.graph = graph
        self.graph.add_node(arn, role=self)

        if source_arn:
            self.graph.add_edge(source_arn, arn)

        if session is None:
            self.sess = boto3.Session()

            self.sess._session._credentials = botocore.credentials.DeferredRefreshableCredentials(  # type: ignore
                refresh_using=lambda: self.credentials(),
                method="liquidswards",
            )
        else:
            self.sess = session

    @property
    def arn(self) -> str:
        return self._arn

    @arn.setter
    def arn(self, arn: str):
        self._arn = arn

        resp = ArnParser().parse_arn(arn)
        resource = resp['resource']
        self.path = '/' + '/'.join(resource.split('/')[1:-1])
        self.name = resp['resource'].split('/')[-1]
        self.account = resp['account']

    def assume(self, target_arn: str) -> 'Optional[Role]':
        try:
            self._assume(target_arn)  # TODO: This cache the returned creds.
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                return None

        return Role(graph=self.graph, arn=target_arn, source_arn=self.arn)

    def _assume(self, target_arn: str) -> Dict[str, str]:
        sts = self.sess.client('sts')
        # TODO: Support external id
        resp = sts.assume_role(RoleArn=target_arn, RoleSessionName='liquidswards')
        return {
            'access_key': resp['Credentials']['AccessKeyId'],
            'secret_key': resp['Credentials']['SecretAccessKey'],
            'token': resp['Credentials']['SessionToken'],
            'expiry_time': resp['Credentials']['Expiration'].isoformat(),
        }

    def credentials(self) -> Optional[Dict[str, str]]:
        graph = nx.subgraph_view(self.graph, filter_edge=hide_edges([(self.arn, self.arn)]))  # Avoid self cycles

        for edge in nx.bfs_predecessors(graph, self.arn, depth_limit=1):
            # TODO: Catch credential error and continue to next
            return self.graph.nodes[edge[0]]['role']._assume(self.arn)
        return None
