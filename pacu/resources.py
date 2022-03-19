import dataclasses
from contextlib import contextmanager
from enum import Enum

from dataclasses import dataclass
from typing import List, Optional

import tinydb.table
from tinydb import where

from pacu import config


class State(Enum):
    Created = "created"
    Added = "added"


@dataclass
class Resource:
    id: str
    state: State


# TODO: Check if resources exist before yielding.
class Resource:
    def __init__(self, _type):
        self.type = _type

    @contextmanager
    def create(self, _id: str):
        try:
            yield
        finally:
            config.resources().insert({'type': self.type, 'id': _id, 'state': State.Created})


    @contextmanager
    def add(self, _id: str):
        try:
            yield
        finally:
            config.resources().insert({'type': self.type, 'id': _id, 'state': State.Added})


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