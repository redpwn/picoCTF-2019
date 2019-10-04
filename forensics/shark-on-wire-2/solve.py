#!/usr/bin/env python3

from scapy.all import *

pcap = rdpcap('./dump.pcap')

b = ''

for packet in pcap:
    b += chr(packet.sport - 5000)

print(b)
