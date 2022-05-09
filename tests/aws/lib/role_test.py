import os

import boto3
import moto

import pytest
import networkx
import dill as pickle

from pacu.aws.lib.role import Role


@pytest.fixture(scope='function')
def graph():
    graph = networkx.Graph()
    role = Role(graph, arn="arn:aws:iam::336983520827:role/test")
    yield graph


def test_graph(graph):
    assert graph is not None


@pytest.fixture(scope='function')
def save(graph):
    save = pickle.dumps(graph)
    yield save


def test_save(save):
    assert save is not None


def test_load(save, graph):
    load = pickle.loads(save)
    assert load != graph


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(scope='function')
def sts(aws_credentials):
    with moto.mock_sts():
        yield boto3.client('sts', region_name='us-east-1')


def test_assume_role_chain(sts):
    graph = networkx.Graph()

    src = Role(graph, "arn:aws:iam::336983520827:role/source", boto3.Session(region_name='us-east-1'))
    second = Role(graph, "arn:aws:iam::336983520827:role/source", boto3.Session(region_name='us-east-1'))
    third = Role(graph, "arn:aws:iam::336983520827:role/dest")

    graph.add_edge(src.arn, second.arn)
    graph.add_edge(second.arn, third.arn)

    # moto seems to return random creds for assume-role
    assert third.credentials()['access_key'].startswith('ASIA')

