# Investigative Reversing 1 - 250 points
## Description

We have recovered a [binary](./mystery) and a few images: [image](./mystery.png), [image2](./mystery2.png), [image3](./mystery3.png). See what you can make of it. There should be a flag somewhere. It's also found in `/problems/investigative-reversing-1_2_72fdacf1b15a239d3327571cd296b954` on the shell server.

## Flag

```
picoCTF{An0tha_1_fc102847}
```

## Solution

Same thing as usual. Let's open it up in Ghidra:

```c

int main(void) {
  FILE *flagtxt;
  FILE *mystery1;
  FILE *mystery2;
  FILE *mystery3;
  long in_FS_OFFSET;
  char flag3;
  int i1;
  int i2;
  int i3;
  char flag [4];
  char local_34;
  char local_33;
  long canary1;
  long canary2;

  canary2 = *(long *)(in_FS_OFFSET + 0x28);

  flagtxt = fopen("flag.txt","r");
  mystery1 = fopen("mystery.png","a");
  mystery2 = fopen("mystery2.png","a");
  mystery3 = fopen("mystery3.png","a");

  if (flagtxt == (FILE *)0x0) {
    puts("No flag found, please make sure this is run on the server");
  }

  if (mystery1 == (FILE *)0x0) {
    puts("mystery.png is missing, please run this on the server");
  }

  fread(flag,0x1a,1,flagtxt);

  fputc((int)flag[1],mystery3);
  fputc((int)(char)(flag[0] + '\x15'),mystery2);
  fputc((int)flag[2],mystery3);

  flag3 = flag[3];

  fputc((int)local_33,mystery3);
  fputc((int)local_34,mystery1);

  i1 = 6;
  while (i1 < 10) {
    flag3 = flag3 + '\x01';
    fputc((int)flag[i1],mystery1);
    i1 = i1 + 1;
  }

  fputc((int)flag3,mystery2);

  i2 = 10;
  while (i2 < 0xf) {
    fputc((int)flag[i2],mystery3);
    i2 = i2 + 1;
  }

  i3 = 0xf;
  while (i3 < 0x1a) {
    fputc((int)flag[i3],mystery1);
    i3 = i3 + 1;
  }

  fclose(mystery1);
  fclose(flagtxt);

  if (canary2 != *(long *)(in_FS_OFFSET + 0x28)) {
    __stack_chk_fail();
  }
  return;
}
```

Great... It's this again. Just another simple one. This time it mixes things up a bit by writing to multiple images.

Here's the solve script:

```python
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
```

This time I just read from the images to try to model the code and do the opposite operations more closely.

```
$ ./solve.py
picoCTF{An0tha_1_fc102847}
```

Bingo!
