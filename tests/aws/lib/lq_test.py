import threading
from queue import Queue

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
def lq_done() -> Lq:
    lq = Lq()
    lq2 = Lq()

    lq.queues.append(Queue())
    lq2.queues.append(Queue())

    lq.depends_on(lq2)
    lq2.depends_on(lq)

    return lq


def test_done(lq_done):
    assert lq_done.running() == False


@pytest.fixture(scope='function')
def lq_running() -> Lq:
    lq = Lq()
    lq2 = Lq()

    q = Queue()
    q.put(1)
    lq.queues.append(q)
    lq2.queues.append(Queue())

    lq.depends_on(lq2)
    lq2.depends_on(lq)

    return lq


def test_running(lq_running):
    assert lq_running.running() == True


# @pytest.fixture(scope='function')
# def each_before(lq):
#     each = lq.each()
#     yield lq
#     assert len(list(each)) == 3
#
#
# def test_broadcast(each_before):
#     for i in range(3):
#         each_before.broadcast(i)


# This test is supposed to block, essentially we don't want lq or lq2 to exit until both have consumed
# their whole queue.
#
# The test above was supposed to ensure calling lq.each() doesn't immediately exit
# to achieve the same thing, however that is not actually what it is testing because lq.each() is a
# generator and list() is called on it after the items have been broadcasted to the queue.
#
# TODO: Figure out how to properly test this.
@pytest.mark.skip(reason="this is supposed to block")
def test_blocking():
    lq = Lq()
    lq2 = Lq()

    lq.depends_on(lq2)
    lq2.depends_on(lq)

    lq.broadcast(1)

    # Should block
    list(lq2.each())
