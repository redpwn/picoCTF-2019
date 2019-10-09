# zero to hero
**Category:** Binary Exploitation

**Points:** 500

**Description:** 
Now you're really cooking. Can you pwn [this]() service?. Connect with `nc 2019shell1.picoctf.com 49928`. [libc.so.6]() [ld-2.29.so]()

----------

We are given the libc base address, so no leaks are needed. All we have to do is get a write.

The issue is that the binary uses libc 2.29, which patches the double free vulnerability (or does it? :o).

Googling common exploits in libc 2.29 didn't help because they involved the use of unsorted bin and/or fastbin, and the checks on chunk size and slot count restricted allocations to tcache.

The vulnerability is that read() overwrites the first byte of the next chunk header with a null byte. If the next chunk has a size header with least significant byte not equal to 0x00, the size of the next chunk changes. 

Before
```
        +-------------------+------------------+
current |        ...        |      0x51        |
        +--------------------------------------+
        |                AAAAAAAA              |
        +-------------------+------------------+
 next   |     AAAAAAAA      |      0x171       |
        +--------------------------------------+
        |                BBBBBBBB              |
        +--------------------------------------+
```

After
```
        +-------------------+------------------+
current |        ...        |      0x51        |
        +--------------------------------------+
        |                AAAAAAAA              |
        +-------------------+------------------+
 next   |     AAAAAAAA      |      0x100       |
        +--------------------------------------+
        |                BBBBBBBB              |
        +--------------------------------------+
```

Assuming that we have freed the next chunk alri'eady, when it is freed again, it will be placed into a separate tcache bin, bypassing the double free patch which only checks for chunks within the same bin. From here, we can control the `fd` pointer of the tcache chunk, doing a standard [tcache poisoning](https://github.com/shellphish/how2heap/blob/master/glibc_2.26/tcache_poisoning.c). To finish, we overwrite `__free_hook` with the win function.

------------

I was under the assumption that chunk headers were 16 bytes long, and chunk size was at offset 8, so the null byte overrun wouldn't do anything. It turns out that this was false. When the previous chunk is in use, the chunk header is actually 8 bytes.

```
       +-------------------+------------------+
-0x010 | data in previous chunk               |
       +-------------------+------------------+
 0x000 | prev data/padding |      0x171       |
       +--------------------------------------+
       |                ...                   |
	   +--------------------------------------+
+0x170 |   next chunk                         |
       +--------------------------------------+
```

Then what about the size of the previous chunk that the heap manager uses to find the previous chunk header during forward consolidation?

This only applies when the previous-in-use flag is 0.
Since the heap manager owns the previous chunk, it can store the size of the previous chunk at the end of the chunk data when the previous chunk is freed.
In short, the chunk header is applicable only when the previous-in-use flag is 0.

```
       +-------------------+------------------+
-0x010 |      data in previous chunk          |
       +-------------------+------------------+
 0x000 | prev chunk size   |      0x170       |
       +--------------------------------------+
       |                ...                   |
	   +--------------------------------------+
+0x170 |   next chunk                         |
       +--------------------------------------+
```