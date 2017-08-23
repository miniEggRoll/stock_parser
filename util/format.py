from datetime import datetime


def parse_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def graphlink(code):
    return 'https://histock.tw/stock/tchart.aspx?m=b&no=' + code


def to_timestamp(a_date):
    if a_date.tzinfo:
        epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
        diff = a_date.astimezone(pytz.UTC) - epoch
    else:
        epoch = datetime(1970, 1, 1)
        diff = a_date - epoch
    return int(diff.total_seconds())
