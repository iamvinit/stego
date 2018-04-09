import fdpttools as ftools
import triencryptbits1 as te
import numpy as np
import math
import argparse
import time
block_size = 2

def encrypt_image(img, strKey):
	
	# stego_img becomes negetive  sometimes when 2 bits of img_freq is replaced 
	# To solve this we make cover image lie from 4-251 

	#add metadata to encrypted secret_img 
	# 1st byte : type of image 1:grayscale 3:rgb
	# 2-3 byte : width
	# 4-5 byte : height
	metadata = bytearray([0] * 5)
	if len(img.shape) > 2:
		metadata[0] = 3
	else:
		metadata[0] = 1
	metadata[1] = img.shape[0] >> 8 
	metadata[2] = img.shape[0] & 0xFF
	metadata[3] = img.shape[1] >> 8 
	metadata[4] = img.shape[1] & 0xFF


	#encrypting the img
	e_img = metadata + te.encrypt(bytearray(img), strKey)
	e_img = np.frombuffer(e_img, dtype='uint8')
	ftools.save_image(np.reshape(e_img[5:],img.shape), "encrypted.png")

def main():

	parser = argparse.ArgumentParser(description = 'Performs Steganography')
	parser.add_argument("coverimage", help="Cover Image path")
	parser.add_argument("key", help="Key to encrypt Secret Image")
	args = parser.parse_args()
	img_path = args.coverimage
	strKey = args.key

	print('Loading ...')
	tick = time.clock()
	#loading
	img = ftools.load_image(img_path)
	tock = time.clock()
	print('Loading Complete. Time taken ' + str(tock - tick))

	print('Encrypting image ...')
	tick = time.clock()
	encrypt_image(img, strKey)
	tock = time.clock()
	print('Encryption Complete. Time Taken ' + str(tock - tick))
	

if __name__ == "__main__":
	main()
