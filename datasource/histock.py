#-*- coding: utf-8 -*-
import json
import ssl
from datetime import timedelta
import os
import numpy

from six.moves import urllib
from util.format import parse_timestamp, graphlink, to_timestamp
from util.log import verbose

COOKIER = urllib.request.HTTPCookieProcessor()
OPENER = urllib.request.build_opener(COOKIER)
CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
urllib.request.install_opener(OPENER)
# Headers to fake a user agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}


class HiStock(object):
    def __init__(self, stock_code, end_date):
        try:
            if not os.path.exists(".history"):
                os.makedirs(".history")
        except Exception as exception:
            print(exception)

        # self.fs = fs
        self.stock_code = stock_code
        self.end_date = end_date
        self.result = []

    def read(self):
        # return self.fs.read(".history/histock_" + self.stock_code)
        stock_file = open(".history/histock_" + self.stock_code)
        raw = stock_file.read()
        stock_file.close()
        return raw

    def write(self, raw):
        # self.fs.write(".history/histock_" + self.stock_code, raw)
        stock_file = open(".history/histock_" + self.stock_code, "w")
        stock_file.write(raw)
        stock_file.close()

    def check_valid(self, raw):
        date_begin = self.end_date.replace(
            hour=0, minute=0, second=0, microsecond=0)
        return raw.find(str(to_timestamp(date_begin) * 1000)) > -1

    def pull(self):
        from_file = True
        raw = None
        try:
            raw = self.read()
        except EnvironmentError:
            from_file = False
            verbose("fail to read", self.stock_code)

        if raw is not None:
            if not self.check_valid(raw):
                from_file = False

        if not from_file:
            raw = self.download()
            self.write(raw)

        price_raw = self.extract_price_raw(raw)
        transaction_raw = self.extract_transaction_raw(raw)

        price_data = json.loads(price_raw)
        transaction_data = json.loads(transaction_raw)
        self.parse(price_data, transaction_data)

    def extract_price_raw(self, raw):
        idx = 0
        while idx < len(raw):
            name_start = raw.find("type", idx)
            name_end = raw.find("\r", name_start)
            data_start = raw.find("data", name_end)
            data_end = raw.find("\r", data_start)

            idx = data_end
            if idx == -1:
                break

            name = raw[name_start:name_end]
            name = name[name.find("'") + 1:name.rfind("'")]
            if name == 'candlestick':
                price_raw = raw[data_start:data_end]
                price_raw = price_raw[price_raw.find(
                    "["):price_raw.rfind("]") + 1]
                return price_raw
        raise Exception("problem parsing price, " + self.stock_code)

    def extract_transaction_raw(self, raw):
        idx = 0
        while idx < len(raw):
            type_start = raw.find("type", idx)
            type_end = raw.find("\r", type_start)
            name_start = raw.find("name", type_end)
            name_end = raw.find("\r", name_start)
            data_start = raw.find("data", type_end)
            data_end = raw.find("\r", data_start)

            idx = data_end
            if idx == -1:
                break

            name = raw[name_start:name_end]
            name = name[name.find("'") + 1:name.rfind("'")]
            if name == '成交量(張)':
                transaction_raw = raw[data_start:data_end]
                transaction_raw = transaction_raw[transaction_raw.find(
                    "["):transaction_raw.rfind("]") + 1]
                return transaction_raw
        raise Exception("problem parsing transaction," + self.stock_code)

    def download(self):
        req = urllib.request.Request(
            graphlink(self.stock_code), headers=HEADERS)
        res = urllib.request.urlopen(req, context=CONTEXT)
        alines = res.read()

        start = alines.find("series: [{")
        end = alines.find("</script>", start)

        substring = alines[start:end]
        return substring

    def parse(self, price_data, transaction_data):
        result = []
        if len(price_data) >= 20:
            j = max(20, len(price_data) - 180)

            while j < len(price_data):
                transaction_count = transaction_data[j][1]
                k = j - 20
                elements = []
                while k < j:
                    elements.append(price_data[k + 1][4])
                    k += 1

                mean = numpy.mean(elements)
                std = numpy.std(elements)

                time = price_data[j][0]
                if parse_timestamp(time) > self.end_date + timedelta(days=1):
                    j += 1
                    continue

                price = price_data[j][4]
                upperbound = mean + 2 * std
                lowerbound = mean - 2 * std
                percent_b = 0.5

                if upperbound != lowerbound:
                    percent_b = (price - lowerbound) / \
                        (upperbound - lowerbound)

                result.append({
                    "time": time,
                    "price": price,
                    "20MA": mean,
                    "std": std,
                    "upperbound": upperbound,
                    "lowerbound": lowerbound,
                    "b": percent_b,
                    "bw": (upperbound - lowerbound) / mean,
                    "transaction_count": transaction_count
                })
                j += 1
        self.result = result
