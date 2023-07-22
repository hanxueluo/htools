#!/usr/bin/env python3
import sys
import time

DELAY=5
time.sleep(DELAY)

def main(argv):
    f = sys.stdin
    if len(argv) > 1:
        f = open(argv[0], "r")
    try:
        l = f.readline()
        while l:
            handle_line(l)
            l = f.readline()
    finally:
        if f != sys.stdin:
            f.close()
    print("Done")

import keyboard
def handle_line(line):
    print(line, end="")
    keyboard.write(line, delay=0.05) 

main(sys.argv[1:])
sys.exit(0)
