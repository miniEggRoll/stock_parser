from __future__ import print_function
import sys

_verbose = "--verbose" in sys.argv

def verbose(*msg):
    if _verbose:
        print(*msg)