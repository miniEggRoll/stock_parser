from __future__ import print_function

import Queue
import threading
from datetime import datetime

from datasource.histock import HiStock
from trend import mean, upperbound
from util.format import graphlink
from util.log import verbose


class App(object):
    def __init__(self, lock):
        self.lock = lock
        self.alive = True
        self.filters = []
        self.companies = []
        self.date = datetime.now()
        self.queue = Queue.Queue()

    def stop(self):
        print("stop app...")
        self.alive = False

    def start(self):
        queue = self.queue
        for code in self.companies:
            queue.put(str(code))

        last_date = self.date

        print(last_date.date(), *self.filters)
        for idx in range(10):
            thd = threading.Thread(
                target=self.do_job, name="Thd" + str(idx))
            thd.daemon = True
            thd.start()

        thd = threading.Thread(target=queue.join, name="app thd")
        thd.daemon = True
        thd.start()

        while thd.isAlive():
            thd.join(1)

    def do_job(self):
        queue = self.queue
        lock = self.lock
        last_date = self.date
        filters = self.filters

        while queue.empty() != True:
            code = queue.get()
            try:
                if not self.alive:
                    continue
                data_source = HiStock(code, last_date)
                data_source.pull()
                data = data_source.result
                with lock:
                    verbose(
                        "---------------------------------------------------------------------")
                    verbose("start checking", code)
                    passed = False
                    if "upperBound" in filters:
                        verbose("- upperBound -")
                        if upperbound.data_filter(data):
                            passed = True
                            print("pass upper bound", code, graphlink(code))
                        verbose("")
                    if "mean" in filters:
                        verbose("- mean -")
                        if mean.data_filter(data):
                            passed = True
                            print("pass mean", code, graphlink(code))
                        verbose("")
                    if not passed:
                        verbose("fail", code)
                    else:
                        verbose("success", code)
            except Exception as exception:
                with lock:
                    print(exception)
                    print("error", code)
            finally:
                queue.task_done()
