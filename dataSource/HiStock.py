import json
import ssl
from datetime import timedelta

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
        self.stock_code = stock_code
        self.end_date = end_date
        self.result = []

    def read(self):
        stock_file = open(".history/histock_" + self.stock_code + ".json")
        raw = stock_file.read()
        stock_file.close()
        return raw

    def write(self, raw):
        stock_file = open(".history/histock_" + self.stock_code + ".json", "w")
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

        data = json.loads(raw)
        self.parse(data)

    def download(self):
        req = urllib.request.Request(
            graphlink(self.stock_code), headers=HEADERS)
        res = urllib.request.urlopen(req, context=CONTEXT)
        alines = res.read()

        start = alines.find("series: [{")
        end = alines.find("</script>", start)

        substring = alines[start:end]
        idx = 0
        while idx < len(substring):
            name_start = substring.find("type", idx)
            name_end = substring.find("\r", name_start)
            data_start = substring.find("data", name_end)
            data_end = substring.find("\r", data_start)

            idx = data_end
            if idx == -1:
                break

            name = substring[name_start:name_end]
            name = name[name.find("'") + 1:name.rfind("'")]
            if name == 'candlestick':
                raw = substring[data_start:data_end]
                raw = raw[raw.find("["):raw.rfind("]") + 1]
                return raw
        raise Exception("problem downloading " + self.stock_code)

    def parse(self, data):
        result = []
        if len(data) >= 20:
            j = max(20, len(data) - 180)

            while j < len(data):
                k = j - 20
                elements = []
                while k < j:
                    elements.append(data[k + 1][4])
                    k += 1

                mean = numpy.mean(elements)
                std = numpy.std(elements)

                time = data[j][0]
                if parse_timestamp(time) > self.end_date + timedelta(days=1):
                    j += 1
                    continue

                price = data[j][4]
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
                    "bw": (upperbound - lowerbound) / mean
                })
                j += 1
        self.result = result
