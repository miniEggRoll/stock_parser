from __future__ import print_function

from six.moves import urllib

from datetime import datetime
import numpy, json, time, ssl, codecs, threading, Queue

_codeList = [1101, 1102, 1103, 1104, 1108, 1109, 1110, 1201, 1203, 1210, 1213, 1215, 1216, 1217, 1218, 1219, 1220, 1225, 1227, 1229, 1231, 1232, 1233, 1234, 1235, 1236, 1256, 1262, 1301, 1303, 1304, 1305, 1307, 1308, 1309, 1310, 1312, 1313, 1314, 1315, 1316, 1319, 1321, 1323, 1324, 1325, 1326, 1337, 1338, 1339, 1340, 1402, 1409, 1410, 1413, 1414, 1416, 1417, 1418, 1419, 1423, 1432, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1449, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1459, 1460, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1503, 1504, 1506, 1507, 1512, 1513, 1514, 1515, 1516, 1517, 1519, 1521, 1522, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1558, 1560, 1568, 1582, 1583, 1589, 1590, 1592, 1598, 1603, 1604, 1605, 1608, 1609, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1626, 1701, 1702, 1704, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1717, 1718, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1762, 1773, 1776, 1783, 1786, 1789, 1802, 1805, 1806, 1808, 1809, 1810, 1817, 1902, 1903, 1904, 1905, 1906, 1907, 1909, 2002, 2006, 2007, 2008, 2009, 2010, 2012, 2013, 2014, 2015, 2017, 2020, 2022, 2023, 2024, 2025, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2038, 2049, 2059, 2062, 2069, 2101, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2109, 2114, 2115, 2201, 2204, 2206, 2207, 2208, 2227, 2228, 2231, 2236, 2239, 2301, 2302, 2303, 2305, 2308, 2311, 2312, 2313, 2314, 2316, 2317, 2321, 2323, 2324, 2325, 2327, 2328, 2329, 2330, 2331, 2332, 2337, 2338, 2340, 2342, 2344, 2345, 2347, 2348, 2349, 2351, 2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2362, 2363, 2364, 2365, 2367, 2368, 2369, 2371, 2373, 2374, 2375, 2377, 2379, 2380, 2382, 2383, 2385, 2387, 2388, 2390, 2392, 2393, 2395, 2397, 2399, 2401, 2402, 2404, 2405, 2406, 2408, 2409, 2412, 2413, 2414, 2415, 2417, 2419, 2420, 2421, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431, 2433, 2434, 2436, 2438, 2439, 2440, 2441, 2442, 2443, 2444, 2448, 2449, 2450, 2451, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461, 2462, 2464, 2465, 2466, 2467, 2468, 2471, 2472, 2474, 2475, 2476, 2477, 2478, 2480, 2481, 2482, 2483, 2484, 2485, 2486, 2488, 2489, 2491, 2492, 2493, 2495, 2496, 2497, 2499, 2501, 2504, 2505, 2506, 2509, 2511, 2514, 2515, 2516, 2520, 2524, 2527, 2528, 2530, 2534, 2535, 2536, 2537, 2538, 2539, 2540, 2542, 2543, 2545, 2546, 2547, 2548, 2597, 2601, 2603, 2605, 2606, 2607, 2608, 2609, 2610, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2633, 2634, 2636, 2637, 2642, 2701, 2702, 2704, 2705, 2706, 2707, 2712, 2722, 2723, 2727, 2731, 2739, 2748, 2801, 2809, 2812, 2816, 2820, 2823, 2832, 2834, 2836, 2838, 2841, 2845, 2849, 2850, 2851, 2852, 2855, 2856, 2867, 2880, 2881, 2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891, 2892, 2897, 2901, 2903, 2904, 2905, 2906, 2908, 2910, 2911, 2912, 2913, 2915, 2923, 2929, 2936, 3002, 3003, 3004, 3005, 3006, 3008, 3010, 3011, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3062, 3090, 3094, 3130, 3149, 3164, 3167, 3189, 3209, 3229, 3231, 3257, 3266, 3296, 3305, 3308, 3311, 3312, 3315, 3321, 3346, 3356, 3376, 3380, 3383, 3406, 3413, 3416, 3419, 3432, 3437, 3443, 3450, 3454, 3481, 3494, 3501, 3504, 3514, 3515, 3518, 3519, 3528, 3532, 3533, 3535, 3536, 3545, 3550, 3557, 3559, 3561, 3576, 3579, 3583, 3588, 3591, 3593, 3596, 3605, 3607, 3617, 3622, 3645, 3653, 3661, 3665, 3669, 3673, 3679, 3682, 3686, 3694, 3698, 3701, 3702, 3703, 3704, 3705, 3706, 3708, 4104, 4106, 4108, 4119, 4133, 4137, 4141, 4142, 4144, 4148, 4164, 4190, 4306, 4414, 4426, 4438, 4526, 4532, 4536, 4545, 4551, 4552, 4555, 4557, 4560, 4720, 4722, 4725, 4737, 4746, 4755, 4763, 4807, 4904, 4906, 4912, 4915, 4916, 4919, 4927, 4930, 4934, 4935, 4938, 4942, 4943, 4952, 4956, 4958, 4960, 4968, 4976, 4977, 4984, 4994, 4999, 5007, 5203, 5215, 5225, 5234, 5243, 5258, 5259, 5264, 5269, 5284, 5285, 5288, 5305, 5388, 5434, 5469, 5471, 5484, 5515, 5519, 5521, 5522, 5525, 5531, 5533, 5534, 5538, 5607, 5608, 5706, 5871, 5880, 5906, 5907, 6005, 6108, 6112, 6115, 6116, 6117, 6120, 6128, 6131, 6133, 6136, 6139, 6141, 6142, 6145, 6152, 6153, 6155, 6164, 6165, 6166, 6168, 6172, 6176, 6177, 6183, 6184, 6189, 6191, 6192, 6196, 6197, 6201, 6202, 6205, 6206, 6209, 6213, 6214, 6215, 6216, 6224, 6225, 6226, 6230, 6235, 6239, 6243, 6251, 6257, 6269, 6271, 6277, 6278, 6281, 6282, 6283, 6285, 6289, 6405, 6409, 6412, 6414, 6415, 6422, 6431, 6442, 6443, 6449, 6451, 6452, 6456, 6464, 6477, 6504, 6505, 6525, 6531, 6533, 6552, 6582, 6605, 8011, 8016, 8021, 8033, 8039, 8046, 8070, 8072, 8081, 8101, 8103, 8105, 8110, 8112, 8114, 8131, 8150, 8163, 8201, 8210, 8213, 8215, 8222, 8249, 8261, 8271, 8341, 8374, 8404, 8411, 8422, 8427, 8429, 8442, 8454, 8463, 8464, 8466, 8467, 8473, 8480, 8481, 8488, 8926, 8940, 8996, 9103, 910322, 910482, 9105, 910708, 910801, 910861, 9110, 911608, 911616, 911619, 911622, 911868, 912000, 912398, 9136, 9157, 9188, 9802, 9902, 9904, 9905, 9906, 9907, 9908, 9910, 9911, 9912, 9914, 9917, 9918, 9919, 9921, 9924, 9925, 9926, 9927, 9928, 9929, 9930, 9931, 9933, 9934, 9935, 9937, 9938, 9939, 9940, 9941, 9942, 9943, 9944, 9945, 9946, 9955, 9958]
# _codeList = [1101, 1102, 1103, 1104, 1108, 1109, 1110, 1201, 1203]
_verbose = False

cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)



_cookie = None
_crumb = None

# Headers to fake a user agent
_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}

def app(env, res):
	lock = threading.Lock()
	
	queue = Queue.Queue()
	for code in _codeList:
		queue.put(str(code))
	for idx in range(10):
		thd = threading.Thread(target=doJob, name="Thd" + str(idx), args=(queue, lock))
		thd.start()
	queue.join()
	# doJob(queue, lock)

def doJob(*args):
	queue = args[0]
	lock = args[1]
	while True:
		if queue.empty():
			break

		code = queue.get()
		try:
			data = parseStock(code, datetime.datetime.now())
			with lock:
				verbose("------------------------------------------------------------------------------")
				verbose("start checking", code)
				if filter(data) == True:
					print("pass", code)
				else:
					verbose("fail", code)
				verbose("------------------------------------------------------------------------------")
		except Exception as e:
			with lock:
				print("error", code, e)
		finally:
			queue.task_done()


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

		verbose("time", getTimeFromTimestamp(today["time"]))

		verbose("bw today:", today["bw"], ", yesterday: ", yesterday["bw"])
		if  today["bw"] < yesterday["bw"] and abs(today["bw"] - yesterday["bw"]) > 0.01:
			return False

		verbose("%b:", today["b"])
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
						elements.append(data[k+1][4])
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
	return result

def getTimeFromTimestamp(timestamp):
	return datetime.fromtimestamp(timestamp/1000)

def verbose(*msg):
	if _verbose == True:
		print(*msg)

app("", "")