#!/bin/bash -e

python base32.py $1 > /tmp/da.txt
cat /tmp/da.txt | python3 overr.py
cat /tmp/da.txt | md5sum
