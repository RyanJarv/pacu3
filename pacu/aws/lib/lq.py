"""
Lq an at least once, in-order queue that delivers both past and future messages to all subscribers.

It's needed to ensure recursive functions can operate on previously delivered events.
"""
import queue
from typing import Any, Generator, List, TypeVar

T = TypeVar('T')


class Lq:
    def __init__(self):
        self.queues: List[queue.Queue] = []
        self.all: List[Any] = []  # Track all broadcast events, so we can redeliver to future subscribers.
        self.lq_dependents = [self]

    def depends_on(self, lq: 'Lq'):
        self.lq_dependents.append(lq)

    def broadcast(self, item: T):
        self.all.append(item)

        for q in self.queues:
            q.put(item)

    def each(self) -> Generator[T, None, None]:
        # Grab the queue first so we error on double-checking an item.
        q: queue.Queue = queue.Queue()
        self.queues.append(q)

        for event in self.all:
            q.put(event)

        while self.running():
            try:
                resp = q.get(block=True, timeout=1)
                yield resp
                q.task_done()
            except queue.Empty:
                continue

    def running(self) -> bool:
        # all dependents need to be checked.
        for lq in self.lq_dependents:
            # If there are no queues self.each() has not been called yet.
            if not lq.queues:
                return True

            # If any task is not done we are still running.
            if any((t.unfinished_tasks for t in lq.queues)):
                return True
        return False

