from __future__ import print_function

from six.moves import urllib

import time
import ssl
import codecs

cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)


_cookie = None
_crumb = None

# Headers to fake a user agent
_headers={
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}

def parseStock():
	'''
	This function perform a query and extract the matching cookie and crumb.
	'''

	# Perform a Yahoo financial lookup on SP500
	req = urllib.request.Request('https://histock.tw/stock/tchart.aspx?no=2317&m=b', headers=_headers)
	gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
	f = urllib.request.urlopen(req, context=gcontext)
	alines = f.read()

	start = alines.find("series: [{")
	end = alines.find("</script>", start)

	substring = alines[start:end]

	idx = 0
	while idx < len(alines):
		nameStart = substring.find("name", idx)
		nameEnd = substring.find("\r", nameStart)
		dataStart = substring.find("data", idx)
		dataEnd = substring.find("\r", dataStart)

		idx = dataEnd
		if idx == -1:
			break
		name = substring[nameStart:nameEnd][7:-2]
		data = substring[dataStart:dataEnd][6:-1]
		print(name)
		print(data)

		file = open("2317_" + name + ".html", "w")
		file.write(data)
		file.close()

parseStock()