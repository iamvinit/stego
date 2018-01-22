import random
import binascii
import base64
from string import ascii_uppercase, ascii_lowercase, digits
def reverseBit(num, noOfBits):
    result = 0
    for i in range(noOfBits):
        result = (result << 1) + (num & 1)
        num >>= 1
    return result

def genTargetBlock(blockVal, sizeOfBlock, optionNo):
	if sizeOfBlock < 1:
		raise ValueError("sizeOfBlock should be greater than 0")
	if optionNo > 3 or optionNo < 0:	
		raise ValueError("optionNo should be between 0 and 3")
	sizeOfBlockinBits = sizeOfBlock * 8
	targetBlockVal = 0
	if optionNo == 0 or optionNo == 1:
		# Taking all the MSBs starting from the source block till the last block generated 
		substreamVal  = blockVal
		targetBlockVal = blockVal & (1 << (sizeOfBlockinBits - 1))
		for sizeOfSubstream in range(sizeOfBlockinBits, 1, -1):
			substreamVal = (substreamVal ^ (substreamVal >> 1)) & ((1 << (sizeOfSubstream - 1)) - 1)
			#print(bin(substreamVal))
			targetBlockVal = targetBlockVal | (substreamVal & (1 << (sizeOfSubstream - 2)))
		if optionNo == 1:
			#Taking all the MSBs starting from the last block generated till the source block 
			targetBlockVal = reverseBit(targetBlockVal, sizeOfBlockinBits)
	elif optionNo == 2 or optionNo == 3:
		#Taking all the LSBs starting from the last block generated till the source block 
		substreamVal  = blockVal
		targetBlockVal = blockVal & 1
		for sizeOfSubstream in range(sizeOfBlockinBits, 1, -1):
			substreamVal = (substreamVal ^ (substreamVal >> 1)) & ((1 << (sizeOfSubstream - 1)) - 1)
			#print(bin(substreamVal))
			targetBlockVal = targetBlockVal | ((substreamVal & 1) << (sizeOfBlockinBits - sizeOfSubstream  + 1))
		if optionNo == 2:
			#Taking all the LSBs starting from the source block till the last block generated
			targetBlockVal = reverseBit(targetBlockVal, sizeOfBlockinBits)

	return targetBlockVal

def generateKey(sizeOfData, maxSizeOfBlock=16):

	#BLock format can be represented with 8 bits
	# First 6 bits from MSB = sizeOfBlockinBytes (max size = 63 bytes)
	# Next 2 bits = optionNo (from 0 to 3)
	if(maxSizeOfBlock > 63):
		raise(ValueError("maxSizeOfBlock cannot be greater than 63 bytes"))
	key = bytearray()
	while sizeOfData > 0:
		sizeOfBlock = random.randrange(1, maxSizeOfBlock + 1)
		optionNo = random.randrange(0, 4)
		# if sizeOfBlock is more than available data change sizeOfBlock
		if sizeOfData < sizeOfBlock:
			sizeOfBlock = sizeOfData
		key.append((sizeOfBlock << 2) | optionNo)	
		sizeOfData = sizeOfData - sizeOfBlock
	return key


# Generates a valid key from passed a ascii encoded string
def generateKeyFromString(sizeOfData, str):
	
	# Characters of str is repeated continously to generate the key for the given data size
	# The last byte is calculated
	# All the size of block must add to sizeOfData

	# Calculate size represented by str
	size_rep = 0
	str_bytes = bytearray(str.encode('ascii'))
	for cbyte in str_bytes:
		size_rep = size_rep + (cbyte >> 2)

	# Calculate number of times str can be added to key
	num_str =  sizeOfData // size_rep

	# add str to key num_str times
	key = str_bytes * num_str
	sizeOfData = sizeOfData - (size_rep * num_str)

	# loop through all characters and add to key. Calculate last char
	i = 0
	while sizeOfData > 0:
		ch = str_bytes[i]
		size_rep_ch = ch >> 2
		if sizeOfData < size_rep_ch:
			ch = (sizeOfData << 2) | (ch & 3)
		key.append(ch)
		sizeOfData = sizeOfData - size_rep_ch
		i = i + 1

	return key


def encrypt(data, strKey):
	#encrypt function for maxSizeOfBlock = 63 bytes
	sizeOfData = len(data)
	key = generateKeyFromString(sizeOfData, strKey)
	encryptedData = bytearray()
	sizeOfDataDone = 0
	data_i = 0 # read from 0th position of data bytearray
	for blockConfig in key:
		sizeOfBlock = blockConfig >> 2
		optionNo = blockConfig & ((1 << 2) - 1)
		blockVal = int.from_bytes(data[data_i : data_i+sizeOfBlock], byteorder='big', signed=False)
		data_i = data_i+sizeOfBlock
		#print(blockConfig)
		#print(sizeOfBlock)
		#print(optionNo)
		targetBlock = genTargetBlock(blockVal, sizeOfBlock, optionNo)
		encryptedData = encryptedData + targetBlock.to_bytes(sizeOfBlock, byteorder='big', signed=False)
		#sizeOfDataDone = sizeOfDataDone + sizeOfBlock
	return encryptedData

def decrypt(data, strKey):
	#decrypt function for maxSizeBlock = 63 bytes
	sizeOfData = len(data)
	key = generateKeyFromString(sizeOfData, strKey)
	decryptedData = bytearray()
	sizeOfDataDone = 0
	data_i = 0 # read from 0th position of data bytearray
	for blockConfig in key:
		sizeOfBlock = blockConfig >> 2
		optionNo = blockConfig & ((1 << 2) - 1)
		if optionNo == 1:
			optionNo = 2
		elif optionNo == 2:
			optionNo = 1
		blockVal = int.from_bytes(data[data_i : data_i+sizeOfBlock], byteorder='big', signed=False)
		data_i = data_i+sizeOfBlock
		#print(blockConfig)
		#print(sizeOfBlock)
		#print(optionNo)
		targetBlock = genTargetBlock(blockVal, sizeOfBlock, optionNo)
		decryptedData = decryptedData + targetBlock.to_bytes(sizeOfBlock, byteorder='big', signed=False)
		#sizeOfDataDone = sizeOfDataDone + sizeOfBlock
	return decryptedData


def encryptStr(strData):
	data = bytearray(strData.encode())
	encryptedData, key =  encrypt(data)

	#converting encrypted data and key to equivalent base64 
	strEncryptedData = base64.b64encode(encryptedData).decode()
	strKey = base64.b64encode(key).decode()

	return (strEncryptedData , strKey)


	
def decryptStr(strEncryptedData, strKey):

	#converting base64 equivalent to bytearray 
	data = bytearray(base64.b64decode(strEncryptedData.encode()))
	key =  bytearray(base64.b64decode(strKey.encode()))

	decryptedData = decrypt(data, key)
	strDecryptedData = decryptedData.decode()
	return strDecryptedData


# data , key = encryptStr("Hello its me")
# print(data)
# print(key)
# print(decryptStr(data, key))


# a = bytearray()
# a.append(97)
# a.append(98)
# enc , key =encrypt(a , 2)
# # enc = base64.b64encode(enc)
# # key = base64.b64encode(key)
# # with open('somefile.txt', 'wb') as the_file:
# #     the_file.write(enc)
# print(enc)
# print(key)

# dec = decrypt(enc, 2, key)

# print(dec)

# testcount = 1
# while True:
	
# 	# dataSize = random.randrange(2,1000000)
# 	dataSize = 1000
# 	data = random.getrandbits(dataSize)
# 	#print(str(data) + " "+ str( dataSize))
# 	encryptedData , key = encrypt(data,dataSize)
# 	dec = (decrypt(encryptedData, 50, key))
# 	#print (dec)
# 	print(str(testcount) + " size= " + str(dataSize))
# 	testcount = testcount + 1
# 	if(data != dec):
# 		print("Error")

# testcount = 1
# while True:
	
# 	# dataSize = random.randrange(2,1000000)
# 	dataSize = 10000
# 	data = ''.join(random.choice(ascii_uppercase + ascii_lowercase + digits) for i in range(dataSize))
# 	#print(data)
# 	encryptedData , key = encryptStr(data)
# 	#print(encryptedData)
# 	print(key)
# 	dec = (decryptStr(encryptedData, key))
# 	#print (dec)
# 	print(str(testcount) + " size= " + str(dataSize))
# 	testcount = testcount + 1
# 	if(data != dec):
# 		print("Error")
