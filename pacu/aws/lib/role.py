import dataclasses
import enum
import botocore.session
import botocore.client
import botocore.config
import botocore.utils
import botocore.auth
import botocore.configloader
import botocore.configloader
import botocore.credentials
import botocore.credentials
import botocore.hooks
import botocore.handlers
from typing import Dict, Optional
import networkx

import boto3

from pacu.lib.graph.access import Access


class RoleState(enum.Enum):
    ActiveState = 0
    RefreshingState = 1
    FailedState = 2


# Inherit graph item
class Role(Access):
    name: str
    arn: str
    account: str

    state: RoleState

    # ExternalId is a list of strings, each item in the list is treated as potentially necessary to assume the role.
    #
    # This mostly is because the trust policy may contain multiple statements. We could be smart about parsing
    # the policy to avoid this if we really wanted to but there may be times when we simply want to
    # try whatever we think might work.
    externalId: str

    creds: botocore.credentials.DeferredRefreshableCredentials
    sess: boto3.Session

    def __init__(self, graph: networkx.Graph, arn: str, session=None):
        self.arn = arn
        self.graph = graph

        if session is None:
            self.sess = boto3.Session()

            self.sess._session._credentials = botocore.credentials.DeferredRefreshableCredentials(  # type: ignore
                refresh_using=lambda: self.credentials(),
                method="liquidswards",
            )
        else:
            self.sess = session

    def assume(self, target_arn: str) -> 'Optional[Role]':
        pass

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
        for edge in networkx.bfs_predecessors(self.graph, self, depth_limit=1):
            # TODO: Catch credential error and continue to next
            return edge[0]._assume(self.arn)
        return None
