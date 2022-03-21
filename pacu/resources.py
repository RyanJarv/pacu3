import dataclasses
from contextlib import contextmanager
from enum import Enum

from dataclasses import dataclass
from typing import List, Optional, Union

import tinydb.table
from tinydb import where

from pacu import config


class State(Enum):
    Created = "created"
    Added = "added"


# TODO: Check if resources exist before yielding.
class Resource:
    def __init__(self, _type):
        self.type = _type

    @contextmanager
    def create(self, _id: str):
        try:
            yield
        finally:
            config.resources().insert({'type': self.type, 'id': _id, 'state': State.Created.value})


    @contextmanager
    def add(self, _id: str):
        try:
            yield
        finally:
            config.resources().insert({'type': self.type, 'id': _id, 'state': State.Added})

    @contextmanager
    def modify(self, _id: str, name: str):
        query = (where('type') == 'ec2.instance') & (where('id') == 'test_resource')

        records = config.resources().search(query)
        assert len(records) == 1
        resource = records[0]

        changes = resource.get('changes', {}).get(name, [])
        try:
            yield lambda c: changes.append(c)
            config.resources().update({'changes': changes}, query)
        finally:
            config.resources().search((where('type') == self.type) & (where('id') == _id))

    @contextmanager
    def delete(self, _id: str):
        try:
            yield
        finally:
            config.resources().remove(
                (where('type') == self.type)
                & (where('id') == _id)
            )


def list(_type: Optional[str]) -> List[tinydb.table.Document]:
    return config.resources().search(where('type') == _type)