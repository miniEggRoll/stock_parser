#-*- coding: utf-8 -*-
from util.log import verbose

# 成交量大於等於一千萬


def data_filter(data):
    today = data[-1]

    result = today["price"] * today["transaction_count"] >= 10000
    return result
