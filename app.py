from __future__ import print_function

import Queue
import threading
from datetime import datetime

from datasource.histock import HiStock
from trend import mean, upperbound, transaction
from util.format import graphlink
from util.log import verbose

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

userIds = ['U0b9a29328a8edbbedfd0400027099c1e', 'U2c645d5f7b78b06a42570d9cfa368531', 'Ua45a5985163a546d23056426944546ed']

class App(object):
    def __init__(self, lock):
        self.lock = lock
        self.alive = True
        self.filters = []
        self.companies = []
        self.date = datetime.now()
        self.queue = Queue.Queue()
        self.messages = []
        self.line_bot_api = LineBotApi('EDD0bDPnx6BFcQVZ2V9MBi7emSgOWvtAasXFDZUGEaDlbUJA6/EP+y9rWUijcbfsqGH/5eICtCXhuTxCsOr0A+cn/C0bJour8lz4skjyqsNPyUEJcueGQ6fWJQvTR2rrFoFMKCvr9O8xoMWY3GR04AdB04t89/1O/w1cDnyilFU=')

    def stop(self, sig, stack):
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

        while thd.isAlive() and self.alive:
            thd.join(1)

        self.appWillStop()

    def appWillStop(self):
        urls = '\r\n'.join(self.messages)
        print('-------------------urls----------------------')
        if len(self.messages) > 0:
            print(urls)
        print('---------------------------------------------')

        msg = TextSendMessage(text=self.date.date().isoformat() + '\r\n' + urls )

        for userId in userIds:
            try:
                self.line_bot_api.push_message(userId, msg)
            except LineBotApiError as e:
                print(e)

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
                    pass_upperbound = False
                    pass_mean = False
                    if "upperBound" in filters:
                        pass_upperbound = upperbound.data_filter(data)
                    if "mean" in filters:
                        pass_mean = mean.data_filter(data)
                    if not (pass_mean or pass_upperbound):
                        verbose("fail", code)
                    else:
                        passed_filters = []
                        if pass_mean:
                            passed_filters.append("mean")
                        if pass_upperbound:
                            passed_filters.append("upperbound")
                        warning = ""
                        if not transaction.data_filter(data):
                            today = data[-1]
                            warning = "do not pass transaction, transaction count: {}, price: {}".format(
                                today["transaction_count"], today["price"])
                        link = graphlink(code)
                        print("{} success: {}, {}, {}".format(
                            code, ",".join(passed_filters), warning, link))
                        if warning == "":
                            self.messages.append(link)

            except Exception as exception:
                with lock:
                    print(exception)
                    print("error", code)
            finally:
                queue.task_done()
