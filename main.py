#!/usr/bin/env python
#-*- coding: utf-8 -*-
import signal
import sys
import threading
from datetime import datetime

from app import App
from companies.listed import listed
from companies.otc import otc

LISTED = listed
OTC = otc

COMPANY_PREFIX = "--company="
DATE_PREFIX = "--date="
FILTER_PREFIX = "--filter="


def find_filters():
    filters = None
    for arg in sys.argv:
        if arg.startswith(FILTER_PREFIX):
            filters = arg[len(FILTER_PREFIX):].split(",")
            break
    if filters is None:
        filters = ["upperBound", "mean"]
    return filters


def find_date():
    date = None
    for arg in sys.argv:
        if arg.startswith(DATE_PREFIX):
            date = datetime.strptime(arg[len(DATE_PREFIX):], "%Y%m%d")
            break
    if date is None:
        date = datetime.now()
    return date


def find_companies():
    companies = None
    for arg in sys.argv:
        if arg.startswith(COMPANY_PREFIX):
            companies = map(int, arg[len(COMPANY_PREFIX):].split(","))
            break
    if companies is None:
        companies = LISTED + OTC
    return companies


if __name__ == '__main__':
    APP = App(threading.Lock())
    APP.companies = find_companies()
    APP.filters = find_filters()
    APP.date = find_date()
    signal.signal(signal.SIGINT, APP.stop)
    APP.start()
