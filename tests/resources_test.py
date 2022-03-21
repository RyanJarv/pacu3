import pytest
from tinydb import where

from pacu import config
from pacu.resources import Resource, State


@pytest.fixture(scope='function')
def resources():
    config.resources().truncate()
    return config.resources()


query = (where('type') == 'ec2.instance') \
        & (where('id') == 'test_resource') \
        & (where('state') == State.Created.value)


def test_create(resources):
    with Resource("ec2.instance").create('test_resource'):
        pass

    records = resources.search(query)

    assert len(records) == 1


def test_modify(resources):
    with Resource("ec2.instance").create('test_resource'):
        pass

    with Resource("ec2.instance").modify('test_resource', 'test_attribute') as change:
        change('test_value')

    records = resources.search(query)

    assert len(records) == 1
    assert records[0] == {
        'changes': ['test_value'],
        'id': 'test_resource',
        'state': 'created',
        'type': 'ec2.instance',
    }