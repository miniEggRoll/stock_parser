from datetime import datetime


def getTimeFromTimestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def graphLink(numberStr):
    return 'https://histock.tw/stock/tchart.aspx?m=b&no=' + numberStr
