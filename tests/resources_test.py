import dataclasses
from typing import List

import pytest
from tinydb import where

from pacu import config
from pacu.repo import BaseResource, Resource, State


@pytest.fixture(scope='function')
def resources():
    config.resources().truncate()
    return config.resources()


@dataclasses.dataclass
class Ec2Instance(BaseResource):
    Changes: List[str] = dataclasses.field(default_factory=list)


query = (where('Type') == Ec2Instance.__name__) \
        & (where('Id') == 'test_resource') \
        & (where('State') == State.Created.value)


def test_create(resources):
    with Resource.new(Ec2Instance(Id='test_resource', State=State.Created)):
        pass

    records = resources.search(query)

    assert len(records) == 1


def test_modify(resources):
    with Resource.new(Ec2Instance(Id='test_resource', State=State.Created)):
        pass

    with Resource.modify(Ec2Instance(Id='test_resource')) as inst:
        inst.Changes += ['test_value']

    records = resources.search(query)

    assert len(records) == 1
    assert records[0] == {
        'Changes': ['test_value'],
        'Id': 'test_resource',
        'State': 'created',
        'Type': 'Ec2Instance',
    }