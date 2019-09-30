# Investigative Reversing 0 - 300 points
## Description

We have recovered a [binary](./mystery) and an [image](./mystery.png). See what you can make of it. There should be a flag somewhere. Its also found in `/problems/investigative-reversing-0_6_2d92ee3bac4838493cb68ec16e086ac6` on the shell server.

## Flag

```
picoCTF{f0und_1t_eeaec48b}
```

## Solution

The first thing I did was to open up the binary in Ghidra:

```c
int main() {
  long lVar1;
  FILE *flagtxt;
  FILE *mysterypng;
  size_t success1;
  long in_FS_OFFSET;
  int iterator;
  int i;
  char flag [4];
  char flag5;
  char flag6;
  char local_29;
  long canary;

  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  flagtxt = fopen("flag.txt","r");
  mysterypng = fopen("mystery.png","a");

  if (flagtxt == (FILE *)0x0) {
    puts("No flag found, please make sure this is run on the server");
  }

  if (mysterypng == (FILE *)0x0) {
    puts("mystery.png is missing, please run this on the server");
  }

  success1 = fread(flag, 0x1a, 1, flagtxt);

  if ((int)success1 < 1) {
    exit(0);
  }
  puts("at insert");
  fputc((int)flag[0],mysterypng);
  fputc((int)flag[1],mysterypng);
  fputc((int)flag[2],mysterypng);
  fputc((int)flag[3],mysterypng);
  fputc((int)flag5,mysterypng);
  fputc((int)flag6,mysterypng);
  iterator = 6;
  while (iterator < 0xf) {
    fputc((int)(char)(flag[iterator] + '\x05'),mysterypng);
    iterator = iterator + 1;
  }
  fputc((int)(char)(local_29 + -3),mysterypng);
  i = 0x10;
  while (i < 0x1a) {
    fputc((int)flag[i],mysterypng);
    i = i + 1;
  }
  fclose(mysterypng);
  fclose(flagtxt);

  if (lVar1 != *(long *)(in_FS_OFFSET + 0x28)) {
    __stack_chk_fail();
  }
  return;
}
```

Okay, so it's basically a simple crackme that appends the "ciphertext" to the input png file.

We can see that it reads `0x1a` bytes to use from the flag, so let's literally just do the exact opposite operations to the last `0x1a` bytes of the png file.

```python
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
```

Predictable.

```
$ ./mystery.py
picoCTF{f0und_1t_eeaec48b}
```
