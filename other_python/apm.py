"""
A little utility to take in a character stream and every minute output the
number of characters that were taken in in that minute
"""

import sys
from datetime import datetime

__PERIOD__ = 60 #seconds
__FLUFF__ = 150 #About how many actual bytes get read per key typed

def main():
    """The main function"""
    if len(sys.argv) < 2:
        print("Give the device file for the keyboard (check /dev/input/by-id/)")
        sys.exit(1)

    with open(sys.argv[1],'rb') as fhi:
        count = 0
        per_start = datetime.now()

        while 1:
            fhi.read(1)
            count += 1

            try_end = datetime.now()
            if (try_end - per_start).seconds >= __PERIOD__:
                print(int(count/__FLUFF__))
                per_start = try_end
                count = 0

main()
