import threading
from typing import List, Any

import networkx

from pacu.aws.lib.lq import Lq
from pacu.lib.utils import run_thread


class RoleSvc:
    lq = Lq()
    threads: List[threading.Thread] = []

    def __init__(self, *, graph: networkx.Graph, plugins: List[Any]):
        self.plugins = plugins
        self.graph = graph

    def run(self):
        for plugin in self.plugins:
            self.threads.append(run_thread(plugin.run))

        self.wait()

    def wait(self):
        for t in self.threads:
            t.join()