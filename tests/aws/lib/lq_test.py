import threading

import pytest

from pacu.aws.lib.lq import Lq


@pytest.fixture(scope='function')
def lq():
    yield Lq()


@pytest.fixture(scope='function')
def broadcasted(lq):
    for i in range(3):
        lq.broadcast(i)
    return lq


def test_each_after(broadcasted):
    assert len(list(broadcasted.each())) == 3


@pytest.fixture(scope='function')
def each_before(lq):
    each = lq.each()
    yield lq
    assert len(list(each)) == 3


def test_broadcast(each_before):
    for i in range(3):
        each_before.broadcast(i)
