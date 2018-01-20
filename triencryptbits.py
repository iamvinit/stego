import random
import binascii,base64
import math
from string import ascii_uppercase, ascii_lowercase, digits
def reverseBit(num, noOfBits):
    result = 0
    for i in range(noOfBits):
        result = (result << 1) + (num & 1)
        num >>= 1
    return result

def genTargetBlock(blockVal, sizeOfBlock, optionNo):
	if sizeOfBlock < 2:
		raise ValueError("sizeOfBlock should be greater than 1")
	if optionNo > 4 or optionNo < 1:
		raise ValueError("optionNo should be between 1 and 4")
	targetBlockVal = 0
	if optionNo == 1 or optionNo == 2:
		# Taking all the MSBs starting from the source block till the last block generated 
		substreamVal  = blockVal
		targetBlockVal = blockVal & (1 << (sizeOfBlock - 1))
		for sizeOfSubstream in range(sizeOfBlock, 1, -1):
			substreamVal = (substreamVal ^ (substreamVal >> 1)) & ((1 << (sizeOfSubstream - 1)) - 1)
			#print(bin(substreamVal))
			targetBlockVal = targetBlockVal | (substreamVal & (1 << (sizeOfSubstream - 2)))
		if optionNo == 2:
			#Taking all the MSBs starting from the last block generated till the source block 
			targetBlockVal = reverseBit(targetBlockVal, sizeOfBlock)
	elif optionNo == 3 or optionNo == 4:
		#Taking all the LSBs starting from the last block generated till the source block 
		substreamVal  = blockVal
		targetBlockVal = blockVal & 1
		for sizeOfSubstream in range(sizeOfBlock, 1, -1):
			substreamVal = (substreamVal ^ (substreamVal >> 1)) & ((1 << (sizeOfSubstream - 1)) - 1)
			#print(bin(substreamVal))
			targetBlockVal = targetBlockVal | ((substreamVal & 1) << (sizeOfBlock - sizeOfSubstream  + 1))
		if optionNo == 3:
			#Taking all the LSBs starting from the source block till the last block generated
			targetBlockVal = reverseBit(targetBlockVal, sizeOfBlock)

	return targetBlockVal

def generateKey(sizeOfData , maxSizeOfBlock = 32):
	noOfBits = 9 
	#BLock format can be represented with 8 bits
	# First 6 bits from MSB = sizeOfBlock (from 2 to 32)
	# Next 3 bits = optionNo (from 1 to 4)
	if maxSizeOfBlock < 2:
		raise(ValueError("maxSizeOfBlock cannot be less than 2"))
	elif maxSizeOfBlock != 32:
		noOfBits = math.ceil(math.log(maxSizeOfBlock + 1,2)) + 3
	key = 0
	while sizeOfData > maxSizeOfBlock:
		sizeOfBlock = random.randrange(2, maxSizeOfBlock+1)
		optionNo = random.randrange(1, 5)
		# check if last block is assigned valid size
		if (sizeOfData - sizeOfBlock) < 2:
			continue
		key = (key << noOfBits) | (sizeOfBlock << 3) | optionNo	
		#print(bin(key))
		sizeOfData = sizeOfData - sizeOfBlock
	#store size and option for last block
	optionNo = random.randrange(1, 5)
	key = (key << noOfBits) | (sizeOfData << 3) | optionNo	
	#print(bin(key))
	return key

def encrypt(data, sizeOfData):
	#encrypt function for maxSizeBlock = 32
	if(sizeOfData < 2):
		raise(ValueError("sizeOfData should be greater than 1 bit"))
	key = generateKey(sizeOfData)
	copyKey = key
	encryptedData = 0
	sizeOfDataDone = 0
	while key > 0:
		blockConfig = key & ((1 << 9) - 1)
		sizeOfBlock = blockConfig >> 3
		optionNo = blockConfig & ((1 << 3) - 1)
		blockVal = data & ((1 << sizeOfBlock) - 1)
		#print(blockConfig)
		#print(sizeOfBlock)
		#print(optionNo)
		key = key >> 9
		data = data >> sizeOfBlock
		targetBlock = genTargetBlock(blockVal, sizeOfBlock, optionNo)
		encryptedData = encryptedData | (targetBlock << sizeOfDataDone)
		sizeOfDataDone = sizeOfDataDone + sizeOfBlock
	return (encryptedData,copyKey)

def decrypt(data, sizeOfData,key ):
	#decrypt function for maxSizeBlock = 32

	decryptedData = 0
	sizeOfDataDone = 0
	while key > 0:
		blockConfig = key & ((1 << 9) - 1)
		sizeOfBlock = blockConfig >> 3
		optionNo = blockConfig & ((1 << 3) - 1)
		if optionNo == 2:
			optionNo = 3
		elif optionNo == 3:
			optionNo = 2
		blockVal = data & ((1 << sizeOfBlock) - 1)
		#print(blockConfig)
		#print(sizeOfBlock)
		#print(optionNo)
		key = key >> 9
		data = data >> sizeOfBlock
		targetBlock = genTargetBlock(blockVal, sizeOfBlock, optionNo)
		decryptedData = decryptedData | (targetBlock << sizeOfDataDone)
		sizeOfDataDone = sizeOfDataDone + sizeOfBlock
	return decryptedData


def encryptStr(strData):
	data = int(binascii.hexlify(strData.encode()),16)
	dataSize =  len(strData) * 8
	encryptedData, key =  encrypt(data, dataSize)

	encryptedData = encryptedData.to_bytes(dataSize//8, byteorder='big', signed=False)
	strEncryptedData = base64.b64encode(encryptedData).decode()

	copyKey = key
	keySize = 0
	while copyKey > 0:
		copyKey = copyKey >> 8
		keySize = keySize + 1
	key = key.to_bytes(keySize, byteorder='big', signed=False)
	strKey = base64.b64encode(key).decode()

	return (strEncryptedData , strKey)

def decryptStr(strEncryptedData, strKey):

	#converting base64 equivalent to bytearray 
	data = bytearray(base64.b64decode(strEncryptedData.encode()))
	dataSize = len(data) * 8
	data = int.from_bytes(data, byteorder='big', signed=False)

	key =  bytearray(base64.b64decode(strKey.encode()))
	key = int.from_bytes(key, byteorder='big', signed=False)

	decryptedData = decrypt(data, dataSize, key)
	decryptedData = decryptedData.to_bytes(dataSize//8, byteorder='big', signed=False)
	strDecryptedData = decryptedData.decode()
	return strDecryptedData



# data , key = encryptStr("Hello its me")
# print(data)
# print(key)
# print(decryptStr(data, key))

# testcount = 1
# while True:
	
# 	# dataSize = random.randrange(2,1000000)
# 	dataSize = 100000
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
