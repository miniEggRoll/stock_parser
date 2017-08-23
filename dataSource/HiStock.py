import json
import ssl
from datetime import timedelta

import numpy

from six.moves import urllib
from util.format import parse_timestamp, graphlink

COOKIER = urllib.request.HTTPCookieProcessor()
OPENER = urllib.request.build_opener(COOKIER)
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

    def pull(self):
        req = urllib.request.Request(
            graphlink(self.stock_code), headers=HEADERS)
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
        res = urllib.request.urlopen(req, context=gcontext)
        alines = res.read()

        start = alines.find("series: [{")
        end = alines.find("</script>", start)

        substring = alines[start:end]
        result = []
        idx = 0
        while idx < len(alines):
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
                data = substring[data_start:data_end]
                data = data[data.find("["):data.rfind("]") + 1]
                data = json.loads(data)

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
                break
        self.result = result
