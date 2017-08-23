#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function

import Queue
import signal
import sys
import threading
from datetime import datetime

from datasource.HiStock import HiStock
from trend import mean, upperbound
from util.format import graphlink
from util.log import verbose

from companies.listed import listed
from companies.otc import otc

LISTED = listed
OTC = otc

COMPANY_PREFIX = "--company="
DATE_PREFIX = "--date="
FILTER_PREFIX = "--filter="

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
                    verbose("---------------------------------------------------------------------")
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

def find_filters():
    filters = None
    for arg in sys.argv:
        if arg.startswith(FILTER_PREFIX):
            filters = arg[len(FILTER_PREFIX):].split(",")
            break
    if filters is None:
        filters = ["upperBound", "mean"]
    return filters
def find_date():
    date = None
    for arg in sys.argv:
        if arg.startswith(DATE_PREFIX):
            date = datetime.strptime(arg[len(DATE_PREFIX):], "%Y%m%d")
            break
    if date is None:
        date = datetime.now()
    return date
def find_companies():
    companies = None
    for arg in sys.argv:
        if arg.startswith(COMPANY_PREFIX):
            companies = map(int, arg[len(COMPANY_PREFIX):].split(","))
            break
    if companies is None:
        companies = LISTED + OTC
    return companies

if __name__ == '__main__':
    APP = App(threading.Lock())
    APP.companies = find_companies()
    APP.filters = find_filters()
    APP.date = find_date()
    signal.signal(signal.SIGINT, APP.stop)
    APP.start()
