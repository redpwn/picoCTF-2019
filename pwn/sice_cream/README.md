# sice_cream - 500 points

## Flag

```
flag{th3_r3al_questi0n_is_why_1s_libc_2.23_still_4_th1ng_62167e9e}
```

## Analysis

```bash
$ strings libc.so.6 | grep GNU
GNU C Library (Ubuntu GLIBC 2.23-0ubuntu11) stable release version 2.23, by Roland McGrath et al.
Compiled by GNU CC version 5.4.0 20160609.
        GNU Libidn by Simon Josefsson

$ checksec sice_cream
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable  FILE
Full RELRO      Canary found      NX enabled    No PIE          No RPATH   RW-RUNPATH   No Symbols      Yes     0               2       sice_cream

```

The libc version is 2.23, meaning that tcache has not been implemented yet. We could also try House of Orange because of less strict checks. Only PIE is disabled, meaning that we will probably have to go for either FSOP or an overwrite on `__malloc_hook` or `__free_hook`. 

Decompiling the binary with Ghidra, there are no checks on the pointer that we free, leading to a double free vulnerability. We also have the ability to print an array in .bss, `name`. Finally, we get a total of 20 mallocs, with a constrained size `(size < 0x58)`.  

## Solution

### Fastbin Dup
We can use [fastbin_dup_into_stack](https://github.com/shellphish/how2heap/blob/master/glibc_2.25/fastbin_dup_into_stack.c) to get a fake chunk in `name`. Note that we have to forge a chunk header initially. 

```
  [ 0xdeadbeef  ] [    0x61    ]
  [ 0x00 (fd)   ] [    ...     ]
                ...               
```
_Fake fastbin chunk_

Note how we set the `fd` pointer of our fake chunk to NULL to make the fastbins a bit cleaner, but this step is probably not necessary. 

### Chunk Forging
After getting a fake chunk, we can edit the `name` array to change our fastbin chunk to an unsorted bin chunk (size > 0x80). The easiest way to fake a chunk is to satisfy the following conditions. 

1. The `prev_in_use` bit of the current chunk is set
2. The `prev_in_use` bit of the next chunk is set
3. THe `prev_in_use` bit of the next next chunk is set

```
0x00  [ 0xdeadbeef  ] [    0x91    ]
      [             ...            ]
      [             ...            ]
      [             ...            ]
0x90  [     ...     ] [    0x11    ]
0xa0  [     ...     ] [    0x11    ]
                    ...               
``` 
*Fake unsorted bin chunk*

Note that the chunk sizes for the next chunk and next next chunk don't have to be valid (chunks of sizes < 0x20 are invalid for 64 bit systems). 

### Libc leak
After freeing the fake chunk, two libc addresses are written to `name`. More specifically, pointers to the unsorted bin are written here. 
```
0x00  [ 0xdeadbeef  ] [    0x91    ]
0x10  [  libc addr  ] [  libc addr ]
      [             ...            ]
      [             ...            ]
0x90  [     ...     ] [    0x11    ]
0xa0  [     ...     ] [    0x11    ]
                    ...               
``` 
*Libc address leak*

We can leak the libc base now by overwriting the first 0x10 bytes of our fake chunk and printing. From here on out, we won't be able to malloc any chunks that are not already in the fastbins (or at least it'll be significantly messier to) because we messed with the unsorted bin. 

### Top Chunk Exploit
The intuition here is to overwrite the top chunk pointer in malloc_state. 
```
struct malloc_state
{
  /* Serialize access.  */
  mutex_t mutex;

  /* Flags (formerly in max_fast).  */
  int flags;

  /* Fastbins */
  mfastbinptr fastbinsY[NFASTBINS];

  /* Base of the topmost chunk -- not otherwise kept in a bin */
  mchunkptr top;

  /* The remainder from the most recent split of a small request */
  mchunkptr last_remainder;   

  /* Normal bins packed as described above */
  mchunkptr bins[NBINS * 2 - 2];

  /* Bitmap of bins */
  unsigned int binmap[BINMAPSIZE];

  /* Linked list */
  struct malloc_state *next;

  /* Linked list for free arenas.  Access to this field is serialized
     by free_list_lock in arena.c.  */
  struct malloc_state *next_free;

  /* Number of threads attached to this arena.  0 if the arena is on
     the free list.  Access to this field is serialized by
     free_list_lock in arena.c.  */
  INTERNAL_SIZE_T attached_threads;

  /* Memory allocated from the system in this arena.  */
  INTERNAL_SIZE_T system_mem;
  INTERNAL_SIZE_T max_system_mem;
};
```

Problematically, there are no valid fastbin chunk headers in libc. The constrained malloc size means we can't forge a chunk of size 0x70 to use the 0x7f addresses typically associated with libc addresses. I guess we'll just have to make our own header then. 

Note that we can control the `fastbinsY` array by doing the fastbin dup exploit. More specifically, we can write any address we want to the corresponding fastbin because we control the `fd` pointer of fastbins. 

```
A2 = alloc(0x48)
B2 = alloc(0x48)

free(A2)
free(B2)
free(A2)

alloc(0x48, payload=p64(address))
alloc(0x48)
alloc(0x48)

# Fastbin for 0x48 (0x50) chunks = address
```
*Slightly modified version of relevant parts of solve.py*

With this, we can write a valid fastbin chunk header into the `malloc_state`, allowing us to overwrite the top chunk pointer. Pointing the top chunk behind `__malloc_hook` allows us to overwrite `__malloc_hook`. 

Small problem: we won't be able to malloc from the top chunk until the unsorted bin is fixed first. To do this, we can forge a chunk with proper unsorted bin addresses so malloc will ignore the unsorted bin chunk. 
```
0x00  [ 0xdeadbeef  ] [    0x21    ]
0x10  [  libc addr  ] [  libc addr ]
      [             ...            ]   
``` 

Activating the malloc hook with the `0xf02a4` one_gadget and a `malloc_printerr` results in a shell.