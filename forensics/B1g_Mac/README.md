# B1g_Mac - 500 points
## Description

Here's a [zip file](https://2019shell1.picoctf.com/static/b0a9a452036cc4c5e41f32ea2fb0acc7/b1g_mac.zip). You can also find the file in /problems/b1g-mac_0_ac4b0dbedcd3b0f0097a5f056e04f97a.

## Flag

```
picoCTF{M4cTim35!}
```

## Solution

Upon reversing the binary, I noticed a function called `_decode` that is never called. To have the challenge solve itself all I needed to do was have this function be called in a debugger.

I opened `main.exe` in x32dbg and set a breakpoint at `0x401B5E`, the address of `call _listdir` (the "encode" function). Once this breakpoint was hit, I overwrote `eip` with the address of `_decode`: `0x401AFE`. Continuing after this prints the flag.
