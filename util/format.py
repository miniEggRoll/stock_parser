from datetime import datetime


def parse_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def graphlink(code):
    return 'https://histock.tw/stock/tchart.aspx?m=b&no=' + code
