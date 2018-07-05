#!/usr/bin/env python3

from collections import defaultdict

f = open("lut_good")

corr = defaultdict(lambda: [])

for line in f:
    words = line.split(' ')

    o = words[0]
    lane0 = words[1]
    lane1 = words[2]
    lane2 = words[3]
    lane3 = words[4]

    if not (lane0 == lane1 and lane0 == lane2 and lane0 == lane3):
        None
        print("shit data", o, lane0, lane1, lane2, lane3)

    if not o == lane0:
        print("mismatch: {:} {:012b} {:}".format(o, int(o, 2) ^ int(lane0, 2), int(o,2) - int(lane0, 2)))
        orig = o[:]
        real = lane0[:]
        if not real in corr[orig]:
            corr[orig].append(real)

print("orig ", "got")
for k, v in corr.items():
    if(len(v) > 1):
        print("fail lut", k, v)
    else:
        print(k, v[0])
