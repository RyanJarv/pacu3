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

    def broadcast(self, item: T):
        self.all.append(item)

        for q in self.queues:
            q.put(item)

    def each(self) -> Generator[T, None, None]:
        # Grab the queue first so we error on double-checking an item.
        q: queue.Queue = queue.Queue()
        self.queues.append(q)

        for event in self.all:
            yield event

        # If any task is not done then we are still running.
        running = any((not t.all_tasks_done for t in self.queues))

        while running:
            yield q.get(block=True)

