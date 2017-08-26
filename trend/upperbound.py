from util.log import verbose
from util.format import parse_timestamp


def log(today, yesterday):
    verbose("-------------")
    verbose("time", parse_timestamp(today["time"]))
    verbose("20MA today:", today["20MA"],
            ", yesterday: ", yesterday["20MA"])
    verbose("bw today:", today["bw"], ", yesterday: ", yesterday["bw"])
    verbose("transaction today:", today["transaction_count"],
            ", yesterday:", yesterday["transaction_count"])


def data_filter(data):
    if len(data) < 4:
        return False

    i = len(data) - 3
    result = True
    while i < len(data) - 1:
        today = data[i]
        yesterday = data[i - 1]

        log(today, yesterday)
        if today["bw"] > 0.2:
            result = False

        if today["bw"] > yesterday["bw"] and abs(today["bw"] - yesterday["bw"]) > 0.035:
            result = False
        i += 1

    today = data[-1]
    yesterday = data[-2]
    log(today, yesterday)
    if today["b"] < 0.9:
        result = False
    if today["bw"] - yesterday["bw"] < 0.035:
        result = False
    return result
