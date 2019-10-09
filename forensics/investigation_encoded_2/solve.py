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