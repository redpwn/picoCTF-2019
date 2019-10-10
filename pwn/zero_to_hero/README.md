# zero to hero - 500

## Description
Now you're really cooking. Can you pwn [this]() service?. Connect with `nc 2019shell1.picoctf.com 49928`. [libc.so.6]() [ld-2.29.so]()

## Analysis
The binary uses glibc version 2.29, which patches the double free vulnerability.

## Solution
We are given the libc base address, so no leaks are needed. All we have to do is get a write.

### House of Poortho

The vulnerability is that read() overwrites the first byte of the next chunk header with a null byte. If the next chunk has a size header with least significant byte not equal to 0x00, the size of the next chunk changes. 

```
        +-------------------+------------------+
current |        ...        |      0x51        |
        +--------------------------------------+
        |                  ...                 |
        +-------------------+------------------+
 next   |        ...        |      0x171       |
        +--------------------------------------+
        |                  ...                 |
        +--------------------------------------+
```
*Before null byte overflow*

```
        +-------------------+------------------+
current |        ...        |      0x51        |
        +--------------------------------------+
        |                AAAAAAAA              |
        +-------------------+------------------+
 next   |     AAAAAAAA      |      0x100       |
        +--------------------------------------+
        |                  ...                 |
        +--------------------------------------+
```
*After null byte overflow*

Assuming that we have freed the next chunk already, when it is freed again, it will be placed into a separate tcache bin, bypassing the double free patch (which only checks for chunks within the same bin). From here, we can control the `fd` pointer of the tcache chunk, doing a standard [tcache poisoning](https://github.com/shellphish/how2heap/blob/master/glibc_2.26/tcache_poisoning.c) to overwrite `__free_hook` with the win function.

Using a single null byte overflow to bypass the new double free protections in glibc 2.29 is a novel exploit. As common with binary exploitation techniques, naming rights go to the person the challenge author. Thus, we would like to refer to this as the House of Poortho, in honor of the problem creator. 