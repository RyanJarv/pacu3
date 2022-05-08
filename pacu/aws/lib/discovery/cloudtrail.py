import logging
import re
import typing
from datetime import datetime, timedelta

import networkx

from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role

if typing.TYPE_CHECKING:
    import mypy_boto3_cloudtrail

arn_re = r'arn:aws:iam::[0-9]{12}:(?:role|assumed-role)/[-a-zA-Z_0-9+=,.@_/]+'

logging = logging.getLogger('cloudtrail')


class CloudTrailRoleSearch:
    def __init__(self, graph: networkx.Graph, discovered_queue: Lq, access_queue: Lq):
        self.graph = graph
        self.discovered_queue = discovered_queue
        self.access_queue = access_queue

    def run(self):
        for role in self.access_queue.each():
            logging.info(f"searching cloudtrail logs with {role.arn}")
            self.search_cloudtrail(role)

    def search_cloudtrail(self, role: Role):
        client = role.sess.client('cloudtrail')
        paginator = client.get_paginator('lookup_events')

        resp = paginator.paginate(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'AssumeRole'
                },
            ],
            StartTime=datetime.now() - timedelta(hours=4),
        )
        for page in resp:
            for event in page['Events']:
                arns = re.findall(arn_re, event['CloudTrailEvent'])

                for arn in filter(self._is_unique, arns):
                    logging.info(f"found arn: {arn}")
                    role = Role(self.graph, arn=arn)
                    self.graph.add_node(arn, role=role)
                    self.discovered_queue.broadcast(role)

    # TODO: Optimize
    def _is_unique(self, arn) -> bool:
        if arn in self.discovered_queue.all:
            return False
        return True
