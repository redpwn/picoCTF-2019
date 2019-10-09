# investigation_encoded_2 - 500 points
## Description

We have recovered a binary and 1 file: image01. See what you can make of it. Its also found in /problems/investigation-encoded-2_0_bf594e1542e760d4c72cc1401d71b3eb on the shell server. NOTE: The flag is not in the normal picoCTF{XXX} format.

## Flag

```
t1m3f1i35000000000003d746a40
```

## Solution

This challenge is similar to investigation_encoded_1, except there is a login function that prevents the binary from executing the encode function. We patch the binary so we can bypass the call to the login function, then do the same approach as investigation_encoded_1: brute force flag until it matches for every possible character with a script.

My solve script is below:
```
import binascii, os

# FLAG: 
# baa3aebb8a3aab8eaa3aebb8ea8eaae2eae8eab8eab8eab8eab8eab8eab8eab8eab8eab8eab8eab8eaae2ab8eae8bae8aeea2bbb8bae8eab80

arr = []
for i in range(48,48+10):
	arr.append(i)
for i in range(97,123):
	arr.append(i)

# # edit as you go (every 2~3 characters) to find the entire flag
for i in range(len(arr)):
	for j in range(len(arr)):
		with open('flag.txt','w') as f:
			f.write('t1m3f1i35000000000003d746a40'+chr(arr[i]))

		os.system('./mystery > /dev/null 2>&1')

		with open('output', 'rb') as f:
		    hexdata = binascii.hexlify(f.read())

		if 'bb8ea8eaae2eae8eab8eab8eab8eab8eab8eab8eab8eab8eab8eab8eab8eaae2ab8eae8bae8aeea2bbb8bae8eab80' in hexdata:
			print(chr(arr[i])+chr(arr[j]),hexdata)
```

Thus, the flag is `t1m3f1i35000000000003d746a40`.