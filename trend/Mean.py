from util.log import verbose
from util.format import parse_timestamp


def data_filter(data):
    if len(data) < 4:
        return False

    i = len(data) - 3
    result = True
    while i < len(data) - 1:
        today = data[i]
        yesterday = data[i - 1]

        verbose("time", parse_timestamp(today["time"]))
        verbose("20MA today:", today["20MA"],
                ", yesterday: ", yesterday["20MA"])
        verbose("bw today:", today["bw"], ", yesterday: ", yesterday["bw"])

        if today["bw"] < yesterday["bw"] and abs(today["bw"] - yesterday["bw"]) > 0.01:
            result = False

        verbose("%b:", today["b"])
        if today["b"] > 0.5:
            result = False
        i += 1

    today = data[-1]
    yesterday = data[-2]
    verbose("time", parse_timestamp(today["time"]))
    verbose("20MA today:", today["20MA"], ", yesterday: ", yesterday["20MA"])
    verbose("bw today:", today["bw"], ", yesterday: ", yesterday["bw"])
    verbose("b today:", today["b"], ", yesterday: ", yesterday["b"])
    if today["b"] < 0.5:
        result = False
    # and abs(today["bw"] - yesterday["bw"]) > 0.005:
    if today["bw"] < yesterday["bw"]:
        result = False

    return result
