import os
from datetime import datetime, timedelta
from unittest import mock

import boto3
import botocore
import botocore.session
import moto
import networkx
import pytest
from botocore.stub import Stubber

from pacu.aws.lib.discovery.cloudtrail import CloudTrailRoleSearch
from pacu.aws.lib.lq import Lq
from pacu.aws.lib.role import Role


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope='function')
def sess(aws_credentials):
    with moto.mock_cloudtrail():
        yield boto3.Session()


def test_run(sess):
    access_queue = Lq()
    discovered_queue = Lq()
    g = networkx.Graph()
    cloudtrail = CloudTrailRoleSearch(graph=g, discovered_queue=discovered_queue, access_queue=access_queue)
    cloudtrail.run()

    access_queue.broadcast(Role(graph=g, arn="arn:aws:iam::123456789012:user/test", session=sess))


## Notes: Not sure what is going on here.
# @mock.patch('boto3.Session.client')
# def test_canary_token_canarytokens_org(client):
#     with Stubber(client.return_value) as stubber:
#         response = {
#           "Events": [
#             {
#               "EventId": "3dd5413c-f4c1-4d0c-8b63-59127f90d26f",
#               "EventName": "AssumeRole",
#               "ReadOnly": "true",
#               "EventTime": datetime(2016, 1, 20, 22, 9),
#               # 'EventTime': datetime.datetime(2022, 4, 20, 8, 52, 15, tzinfo=tzlocal()),
#               "EventSource": "sts.amazonaws.com",
#               "Resources": [
#                 {
#                   "ResourceType": "AWS::IAM::AccessKey",
#                   "ResourceName": "ASIAXXXXXXXXXXXXXXXX",
#                 },
#                 {
#                   "ResourceType": "AWS::STS::AssumedRole",
#                   "ResourceName": "test-role"
#                 },
#                 {
#                   "ResourceType": "AWS::IAM::Role",
#                   "ResourceName": "arn:aws:iam::123456789012:role/service-role/test-role"
#                 }
#               ],
#               "CloudTrailEvent": """
#               {
#                   "eventVersion": "1.08",
#                   "userIdentity": {
#                     "type": "AWSService",
#                     "invokedBy": "lambda.amazonaws.com"
#                   },
#                   "eventTime": "2022-04-21T01:52:21Z",
#                   "eventSource": "sts.amazonaws.com",
#                   "eventName": "AssumeRole",
#                   "awsRegion": "us-east-1",
#                   "sourceIPAddress": "lambda.amazonaws.com",
#                   "userAgent": "lambda.amazonaws.com",
#                   "requestParameters": {
#                     "roleArn": "arn:aws:iam::123456789012:role/service-role/test-role",
#                     "roleSessionName": "test-role"
#                   },
#                   "responseElements": {
#                     "credentials": {
#                       "accessKeyId": "test-access-key",
#                       "sessionToken": "test-session-token",
#                       "expiration": "Apr 21, 2022, 1:52:21 PM"
#                     }
#                   },
#                   "requestID": "12345678-1234-1234-1234-123456789012",
#                   "eventID": "22345678-1234-1234-1234-123456789012",
#                   "readOnly": true,
#                   "resources": [
#                     {
#                       "accountId": "123456789012",
#                       "type": "AWS::IAM::Role",
#                       "ARN": "arn:aws:iam::123456789012:role/service-role/test-role"
#                     }
#                   ],
#                   "eventType": "AwsApiCall",
#                   "managementEvent": true,
#                   "recipientAccountId": "123456789012",
#                   "sharedEventID": "12345678-1234-1234-1234-123456789012",
#                   "eventCategory": "Management"
#                 }
#               """
#             }
#           ],
#           'ResponseMetadata': {
#               'RequestId': '6d4e6f55-5587-4d21-a98d-5de694419265',
#               'HTTPStatusCode': 200,
#               'HTTPHeaders': {
#                   'x-amzn-requestid': '6d4e6f55-5587-4d21-a98d-5de694419265',
#                   'content-type': 'application/x-amz-json-1.1',
#                   'content-length': '9956',
#                   'date': datetime(2016, 1, 20, 22, 9),
#               },
#               'RetryAttempts': 0
#           },
#         }
#
#
#         expected_params = {
#             "LookupAttributes": [{
#                 'AttributeKey': 'EventName',
#                 'AttributeValue': 'AssumeRole'
#             }],
#             "StartTime": datetime.now() - timedelta(hours=4),
#             "EndTime": datetime.now(),
#         }
#         stubber.add_response('lookup_events', response, expected_params)
#
#         # response = {
#         #   'ResponseMetadata': {
#         #       'RequestId': '6d4e6f55-5587-4d21-a98d-5de694419265',
#         #       'HTTPStatusCode': 200,
#         #       'HTTPHeaders': {
#         #           'x-amzn-requestid': '6d4e6f55-5587-4d21-a98d-5de694419265',
#         #           'content-type': 'application/x-amz-json-1.1',
#         #           'content-length': '9956',
#         #           'date': datetime(2016, 1, 20, 22, 9),
#         #       },
#         #       'RetryAttempts': 0
#         #   },
#         # }
#         #
#         # stubber.add_response(
#         #     'list_domains',
#         #     service_response=response,
#         #     # expected_params={},
#         # )
#
#         access_queue = Lq()
#         discovered_queue = Lq()
#         g = networkx.Graph()
#         cloudtrail = CloudTrailRoleSearch(graph=g, discovered_queue=discovered_queue, access_queue=access_queue)
#         cloudtrail.run()
#
#         access_queue.broadcast(Role(graph=g, arn="arn:aws:iam::123456789012:user/test", session=sess))
#         client.return_value = botocore.session.get_session().create_client('cloudtrail')
