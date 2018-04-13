import fdpttools as ftools
import triencryptbytesn as te
import numpy as np
import math
import argparse
import time
block_size = 2

def encrypt_image(img, strKey):

	#encrypting the img
	e_img = te.encrypt(bytearray(img), strKey)
	e_img = np.frombuffer(e_img, dtype='uint8')
	e_img = np.reshape(e_img, img.shape)
	return e_img

def multiple_encrypt_image(img,strKey, numIteration):
	for i in range(1,numIteration+1):
		print("PASS "+str(i))
		te.changeSizeOfBlockMul(i*2)
		img = encrypt_image(img, strKey)
	return img

def main(img_path, strKey, outputfilename):

	
	print('Loading ...')
	tick = time.clock()
	#loading
	img = ftools.load_image(img_path)
	tock = time.clock()
	print('Loading Complete. Time taken ' + str(tock - tick))

	print('Encrypting image ...')
	tick = time.clock()
	e_img = multiple_encrypt_image(img, strKey, 10)
	ftools.save_image(e_img, outputfilename)
	tock = time.clock()
	print('Encryption Complete. Time Taken ' + str(tock - tick))
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Performs Encryption')
	parser.add_argument("img_path", help="Image path")
	parser.add_argument("key", help="Key to encrypt Secret Image")
	parser.add_argument("-o", "--outputfilename", help="Output file name")
	args = parser.parse_args()
	img_path = args.img_path
	strKey = args.key
	if(args.outputfilename):
		outputfilename = args.outputfilename
	else:
		outputfilename = 'encrypted.png'
	main(img_path, strKey, outputfilename)
