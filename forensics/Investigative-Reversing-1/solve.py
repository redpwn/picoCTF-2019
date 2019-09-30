#!/usr/bin/env python3

from io import BytesIO as bio

mystery1 = bio(open('mystery.png', 'rb').read()[::-1])
mystery2 = bio(open('mystery2.png', 'rb').read()[::-1])
mystery3 = bio(open('mystery3.png', 'rb').read()[::-1])

read = lambda s, x : ord(s.read(x))
rrange = lambda a, b : reversed(range(a, b))

flag = [0] * 0x1a

for i in rrange(0xf, 0x1a):
    flag[i] = read(mystery1, 1)

for i in rrange(10, 0xf):
    flag[i] = read(mystery3, 1)

flag[3] = read(mystery2, 1) - (10 - 6) * 0x1

for i in rrange(6, 10):
    flag[i] = read(mystery1, 1)

flag[5] = read(mystery1, 1)
flag[4] = read(mystery3, 1)
flag[2] = read(mystery3, 1)
flag[0] = read(mystery2, 1) - 0x15
flag[1] = read(mystery3, 1)

print(bytes(flag).decode('utf-8', errors = 'replace'))
