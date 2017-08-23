from __future__ import print_function
import sys

VERBOSE = "--verbose" in sys.argv

def verbose(*msg):
    if VERBOSE:
        print(*msg)
