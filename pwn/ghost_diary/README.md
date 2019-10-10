# Ghost_Diary - 500 points

## Flag

```
picoCTF{nu11_byt3_Gh05T_41a29ece}
```

## Analysis
```
$ ldd ghostdiary
    linux-vdso.so.1 (0x00007ffcabdd4000)
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ff81dd18000)
    /lib64/ld-linux-x86-64.so.2 (0x00007ff81e30c000)
    
$ strings /lib/x86_64-linux-gnu/libc.so.6 | grep GNU
GNU C Library (Ubuntu GLIBC 2.27-3ubuntu1) stable release version 2.27.
Compiled by GNU CC version 7.3.0.

$ checksec ghostdiary
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

The libc version is 2.27 which implies the use of tcache with very little security checks. All protections are enabled, implying a heap only exploit. 

We can only malloc 20 chunks at a time (which is not a really big concern). There is also a rather interesting constraint on malloc size, `(size <= 0xf0 || (size >= 0x110 && size <= 0x1e0)`. There is a null byte overflow in the edit function. In addition, we can print any chunk, regardless of if it's freed or not, which we will use to get a libc leak.

## Solution

### Libc Leak
Note that tcache bins prevent us from getting a leak normally by freeing unsorted bin. However, each tcache bin can only hold a maximum of 7 chunks, letting us easily overflow it. We create 8 chunks in the unsorted bin range, and free them all. The last freed chunk will have a libc address, which we can leak.

### Null Byte Poisoning

As a broad overview, we shrink the middle chunk and use backwards consolidation to get overlapping chunks. Throughout this exploit, we will need to ensure that the tcache is filled, or else our freed chunks will go into the tcache and not unsorted bins. 

Note: This technique relies on exploiting the shrunken chunk size, **not** forging the `prev_in_use` bit. 

In order to perform null byte poisoning, we need 3 chunks. 

```
0x00   [ 0xdeadbeef  ] [    0x121   ]  A
       [             ...            ]
       [             ...            ]
0x120  [     ...     ] [    0x121   ]  B
       [             ...            ]
       [             ...            ]
0x240  [     ...     ] [    0x121   ]  C
       [             ...            ]
       [             ...            ]
                    ...               
``` 
*Initial setup*

We eventually want to shrink chunk B by overwriting the least significant byte of the size header with 0x00. Thus, the new size of B becomes 0x100. Before we do this, we will need to write some the `prev_size` value to complete our forging of B's fake size (or else it will error when we malloc). We will then free B to setup the backwards consolidation later. 

```
0x00   [    0xdeadbeef    ] [      0x121     ]  A
       [                  ...                ]
       [                  ...                ]
0x120  [        ...       ] [      0x121     ]  B [ FREE ]
       [                  ...                ]
       [                  ...                ]
0x210  [ 0x100 prev_size  ] [      ...       ]    [ FAKE HEADER ]
       [                  ...                ]
       [                  ...                ]
0x240  [ 0x120 prev_size  ] [      0x120     ]  C
       [                  ...                ]
       [                  ...                ]
                          ...               
``` 
*Prior to null byte overflow*

Note that malloc does not check the size value in the fake header. We then abuse the null byte overflow to change B's size. 


```
0x00   [    0xdeadbeef    ] [      0x121     ]  A [ FREE ]
       [                  ...                ]
       [                  ...                ]
0x120  [        ...       ] [      0x100     ]  B [ FREE ]
       [                  ...                ]
       [                  ...                ]
0x210  [ 0x100 prev_size  ] [      ...       ]    [ FAKE HEADER ]
       [                  ...                ]
       [                  ...                ]
0x240  [ 0x120 prev_size  ] [      0x120     ]  C
       [                  ...                ]
       [                  ...                ]
                          ...               
``` 
*After null byte overflow*

If we malloc again, we'll get a chunk from B. 

```
0x00   [    0xdeadbeef    ] [      0x121     ]  A   
       [                  ...                ]
       [                  ...                ]
0x120  [        ...       ] [      0x91      ]  B1 
       [                  ...                ]
       [                  ...                ]
0x1a0  [        ...       ] [      0x70      ]  B2  [ FREE ]
       [                  ...                ]
       [                  ...                ]
0x210  [ 0x70 prev_size   ] [      ...       ]      [ FAKE HEADER ]
       [                  ...                ]
       [                  ...                ]
0x240  [ 0x120 prev_size  ] [      0x120     ]  C
       [                  ...                ]
       [                  ...                ]
                          ...               
``` 
*After malloc 0x88*

We malloc again to get our chunk that we'll collapse over. 

```
0x00   [    0xdeadbeef    ] [      0x121     ]  A   
       [                  ...                ]
       [                  ...                ]
0x120  [        ...       ] [      0x91      ]  B1 
       [                  ...                ]
       [                  ...                ]
0x1a0  [        ...       ] [      0x41      ]  B2 
       [                  ...                ]
       [                  ...                ]
0x1e0  [        ...       ] [      0x30      ]  B3  [ FREE ]
       [                  ...                ]
       [                  ...                ]
0x210  [ 0x30 prev_size   ] [      ...       ]      [ FAKE HEADER ]
       [                  ...                ]
       [                  ...                ]
0x240  [ 0x120 prev_size  ] [      0x120     ]  C
       [                  ...                ]
       [                  ...                ]
                          ...               
``` 
*After malloc 0x38*

We then free B1 to ensure that a proper `prev_size` header is written, to bypass the following check in malloc.c. 

```c
if (__builtin_expect (chunksize(P) != prev_size (next_chunk(P)), 0))      \
      malloc_printerr ("corrupted size vs. prev_size");    
```

Note that this `prev_size` check only checks against the next chunk from the perspective of the chunk being backwards consolidated into, B1, as opposed to checking against the `prev_size` of the original chunk being freed, C. In other words, it checks if `size(B1) == prev_size(B1 + size(B1))`. 

```
0x00   [    0xdeadbeef    ] [      0x121     ]  A   
       [                  ...                ]
       [                  ...                ]
0x120  [        ...       ] [      0x91      ]  B1  [ FREE ]
       [                  ...                ]
       [                  ...                ]
0x1a0  [        0x90      ] [      0x40      ]  B2  
       [                  ...                ]
       [                  ...                ]
0x1e0  [        ...       ] [      0x30      ]  B3  [ FREE ]
       [                  ...                ]
       [                  ...                ]
0x210  [ 0x30 prev_size   ] [      ...       ]      [ FAKE HEADER ]
       [                  ...                ]
       [                  ...                ]
0x240  [ 0x120 prev_size  ] [      0x120     ]  C
       [                  ...                ]
       [                  ...                ]
                          ...               
``` 
*After freeing B1*

We can then free C to backwards consolidate over B2, resulting in overlapping chunks. With overlappping chunks, we can free B2 (so it goes in the tcache), and then overwrite the `fd` pointer to `__free_hook`. We then overwrite `__free_hook` with `system`, and free a chunk with `"/bin/sh\x00"` in it. 