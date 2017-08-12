from __future__ import print_function

from six.moves import urllib

import numpy
import json
import time
import ssl
import codecs
import datetime

cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)


_cookie = None
_crumb = None

# Headers to fake a user agent
_headers={
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}

def test():
	data = parseStock("3227", datetime.datetime(2017, 7, 25, 23, 59))
	saveFile(data, "data.csv")
	if filter(data) == True:
		print("found")
	else:
		print("fail")

def saveFile(result, filename):
	timeOutput = ""
	maOutput = ""
	upperboundOutput = ""
	lowerboundOutput = ""

	for record in result:
		timeOutput = timeOutput + str(record["time"]) + ","
		maOutput = maOutput + str(record["20MA"]) + ","
		upperboundOutput = upperboundOutput + str(record["upperbound"]) + ","
		lowerboundOutput = lowerboundOutput + str(record["lowerbound"]) + ","

	timeOutput = timeOutput[0:-1]
	maOutput = maOutput[0:-1]
	upperboundOutput = upperboundOutput[0:-1]
	lowerboundOutput = lowerboundOutput[0:-1]

	file = open(filename, "w")
	file.write(timeOutput)
	file.write("\r")
	file.write(maOutput)
	file.write("\r")
	file.write(upperboundOutput)
	file.write("\r")
	file.write(lowerboundOutput)
	file.write("\r")
	file.close()


def filter(data):
	if len(data) < 4:
		return False

	i = len(data) - 3
	while i < len(data):
		today = data[i]
		yesterday = data[i - 1]

		print("time", getTimeFromTimestamp(today["time"]))

		print("bw today:", today["bw"], ", yesterday: ", yesterday["bw"])
		if  today["bw"] < yesterday["bw"] and abs(today["bw"] - yesterday["bw"]) > 0.01:
			return False

		print("%b:", today["b"])
		if today["b"] < 0.5:
			return False
		i += 1

	today = data[-1]
	yesterday = data[-2]
	if today["b"] < 0.95:
		return False
	if today["bw"] < yesterday["bw"]:
		return False

	return True


def parseStock(numberStr, endDate):
	req = urllib.request.Request('https://histock.tw/stock/tchart.aspx?no=' + numberStr + '&m=b', headers=_headers)
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
			data = data[data.find("["):data.rfind("]")+1]
			data = json.loads(data)

			if len(data) >= 20:
				j = max(20, len(data) - 180)

				while j < len(data):
					k = j - 20
					elements = []
					while k < j	:
						elements.append(data[k][4])
						k += 1

					mean = numpy.mean(elements)
					std = numpy.std(elements)

					time = data[j][0]
					if getTimeFromTimestamp(time) > endDate:
						j += 1
						continue

					price = data[j][4]
					ub = mean + 2*std
					lb = mean - 2*std

					result.append({
						"time": time,
						"price": price,
						"20MA": mean,
						"std": std,
						"upperbound": ub,
						"lowerbound": lb,
						"b": (price - lb)/(ub - lb),
						"bw": (ub - lb)/mean
					})
					j += 1
			break
	print("data dumped")
	return result

def getTimeFromTimestamp(timestamp):
	return datetime.datetime.fromtimestamp(timestamp/1000)

test()