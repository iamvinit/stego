import fdpttools as ftools
import triencryptbytesn as te
import numpy as np
import math
import argparse
import time
block_size = 2

def decrypt_image(img, strKey):

	#encrypting the img
	e_img = te.decrypt(bytearray(img), strKey)
	e_img = np.frombuffer(e_img, dtype='uint8')
	e_img = np.reshape(e_img, img.shape)
	return e_img

def main(img_path, strKey, outputfilename):

	
	print('Loading ...')
	tick = time.clock()
	#loading
	img = ftools.load_image(img_path)
	tock = time.clock()
	print('Loading Complete. Time taken ' + str(tock - tick))

	print('Decrypting image ...')
	tick = time.clock()
	e_img = decrypt_image(img, strKey)
	ftools.save_image(e_img, outputfilename)
	tock = time.clock()
	print('Decryption Complete. Time Taken ' + str(tock - tick))
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Performs Decryption')
	parser.add_argument("img_path", help="Encrypted Image path")
	parser.add_argument("key", help="Key to encrypt Secret Image")
	parser.add_argument("-o", "--outputfilename", help="Output file name")
	args = parser.parse_args()
	img_path = args.img_path
	strKey = args.key
	if(args.outputfilename):
		outputfilename = args.outputfilename
	else:
		outputfilename = 'decrypted.png'
	main(img_path, strKey, outputfilename)
