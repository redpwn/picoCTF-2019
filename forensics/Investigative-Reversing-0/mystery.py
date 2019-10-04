#!/usr/bin/env python3

# these are the last few bytes of the file
o = [int(x, 16) for x in '70 69 63 6f 43 54 4b 80 6b 35 7a 73 69 64 36 71 5f 65 65 61 65 63 34 38 62 7d'.split(' ')]

flag = []

for i in range(5):
    flag.append(o.pop(0))

for i in range(6, 0xf + 1):
    flag.append(o.pop(0) - 5)

flag.append(o.pop(0) + 3)

for i in range(0x10, 0x1a):
    flag.append(o.pop(0))

print(bytes(flag).decode())
