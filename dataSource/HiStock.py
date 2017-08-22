from six.moves import urllib
from datetime import datetime, timedelta
import json
import numpy
import ssl
from util import getTimeFromTimestamp, graphLink

cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)
# Headers to fake a user agent
_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}


class HiStock:
    def __init__(self, stockCode, endDate):
        self.stockCode = stockCode
        self.endDate = endDate

    def pullData(self):
        req = urllib.request.Request(
            graphLink(self.stockCode), headers=_headers)
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
        f = urllib.request.urlopen(req, context=gcontext)
        alines = f.read()

        start = alines.find("series: [{")
        end = alines.find("</script>", start)

        substring = alines[start:end]
        result = []
        idx = 0
        while idx < len(alines):
            nameStart = substring.find("type", idx)
            nameEnd = substring.find("\r", nameStart)
            dataStart = substring.find("data", nameEnd)
            dataEnd = substring.find("\r", dataStart)

            idx = dataEnd
            if idx == -1:
                break

            name = substring[nameStart:nameEnd]
            name = name[name.find("'") + 1:name.rfind("'")]
            if name == 'candlestick':
                data = substring[dataStart:dataEnd]
                data = data[data.find("["):data.rfind("]") + 1]
                data = json.loads(data)

                if len(data) >= 20:
                    j = max(20, len(data) - 180)

                    while j < len(data):
                        k = j - 20
                        elements = []
                        while k < j	:
                            elements.append(data[k + 1][4])
                            k += 1

                        mean = numpy.mean(elements)
                        std = numpy.std(elements)

                        time = data[j][0]
                        if getTimeFromTimestamp(time) > self.endDate + timedelta(days=1):
                            j += 1
                            continue

                        price = data[j][4]
                        ub = mean + 2 * std
                        lb = mean - 2 * std
                        b = 0.5

                        if ub != lb:
                            b = (price - lb) / (ub - lb)

                        result.append({
                            "time": time,
                            "price": price,
                            "20MA": mean,
                            "std": std,
                            "upperbound": ub,
                            "lowerbound": lb,
                            "b": b,
                            "bw": (ub - lb) / mean
                        })
                        j += 1
                break
        self.result = result
