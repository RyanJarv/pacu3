import logging
import re
import typing
from datetime import datetime, timedelta

import networkx
from botocore.exceptions import ClientError

from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role

if typing.TYPE_CHECKING:
    import mypy_boto3_iam

arn_re = r'arn:aws:iam::[0-9]{12}:(?:role|assumed-role)/[-a-zA-Z_0-9+=,.@_/]+'

logging = logging.getLogger('cloudtrail')


class ListRolesSearch:
    def __init__(self, graph: networkx.Graph, discovered_queue: Lq, access_queue: Lq):
        self.graph = graph
        self.discovered_queue = discovered_queue
        self.access_queue = access_queue

    def run(self):
        role: Role
        for role in self.access_queue.each():
            logging.info(f"listing roles for account {role.account}")
            try:
                self.list_roles(role)
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logging.info(f"unable to call ListRoles with {role.arn}")

    def list_roles(self, role: Role):
        client = role.sess.client('iam')
        paginator = client.get_paginator('list_roles')

        for page in paginator.paginate():
            for role in page['Roles']:
                arn = role['Arn']
                if not self._is_unique(arn):
                    continue

                logging.info(f"found arn: {arn}")
                role = Role(self.graph, arn=arn)
                self.discovered_queue.broadcast(role)

    # TODO: Optimize
    def _is_unique(self, arn) -> bool:
        for role in self.discovered_queue.all:
            if arn == role.arn:
                return False
        return True
