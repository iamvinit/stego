import fdpttools as ftools
import triencryptbytes as te
import numpy as np
import math
import argparse
import time
block_size = 2

# hides 2 bit of cover_img with sec_img
def hide_image(cover_img, sec_img, strKey):
	if np.prod(sec_img.shape) > (np.prod(cover_img.shape) / 4 - 5):
		raise ValueError("secret image too large to be hidden in cover image")

	# stego_img becomes negetive  sometimes when 2 bits of cover_img_freq is replaced 
	# To solve this we make cover image lie from 4-251 
	cover_img = np.copy(cover_img)
	cover_img[ cover_img > 251] = 251
	cover_img[ cover_img < 4] = 4

	#add metadata to encrypted secret_img 
	# 1st byte : type of image 1:grayscale 3:rgb
	# 2-3 byte : width
	# 4-5 byte : height
	metadata = bytearray([0] * 5)
	if len(sec_img.shape) > 2:
		metadata[0] = 3
	else:
		metadata[0] = 1
	metadata[1] = sec_img.shape[0] >> 8 
	metadata[2] = sec_img.shape[0] & 0xFF
	metadata[3] = sec_img.shape[1] >> 8 
	metadata[4] = sec_img.shape[1] & 0xFF


	#encrypting the sec_img
	e_sec_img = metadata + te.encrypt(bytearray(sec_img), strKey)
	e_sec_img = np.frombuffer(e_sec_img, dtype='uint8')

	#dividing encrypted sec_img into np array of 2 bits
	e_sec_img =  np.repeat(e_sec_img, 4, axis = 0)
	e_sec_img[::4] = e_sec_img[::4] >> 6
	e_sec_img[1::4] = (e_sec_img[1::4] >> 4) & 3
	e_sec_img[2::4] = (e_sec_img[2::4] >> 2) & 3
	e_sec_img[3::4] = e_sec_img[3::4] & 3
	#ftools.save_image(np.reshape(e_sec_img,(512,512)),"encrypted.png")
	e_sec_img_size = len(e_sec_img)

	#converting cover_img to frequency domain
	cover_img_freq = ftools.fdpt(cover_img,block_size, shape = (-1))

	#hiding encrypted sec_img in cover_img_freq
	stego_img_freq = cover_img_freq
	stego_img_freq[:e_sec_img_size] = ((cover_img_freq[:e_sec_img_size] >> 2) << 2) | e_sec_img
	
	#converting stego_img_freq to spatial domain
	stego_img = ftools.ifdpt(stego_img_freq,block_size, shape = cover_img.shape)

	return stego_img

def unhide_image(stego_img, strKey):

	#converting stego_img to frequency domain
	stego_img_freq = ftools.fdpt(stego_img,block_size)

	#extract sec_img
	stego_img_freq = (np.reshape(stego_img_freq, (-1,4)) & 0b11).astype(np.uint8)
	stego_img_freq[:,0]  = (stego_img_freq[:,0] << 6) | (stego_img_freq[:,1] << 4) | (stego_img_freq[:,2] << 2) | stego_img_freq[:,3] 

	# extract metadata
	# 1st byte : type of image 0:grayscale 1:rgb
	# 2-3 byte : width
	# 4-5 byte : height
	metadata = stego_img_freq[:5,0]
	sec_img_width = metadata[1] << 8 | metadata[2]
	sec_img_height = metadata[3] << 8 | metadata[4]
	sec_img_shape = (sec_img_width,sec_img_height,metadata[0])

	#decrypt sec_img
	sec_img = te.decrypt(bytearray(stego_img_freq[5:np.prod(sec_img_shape)+5,0]), strKey)
	sec_img = np.frombuffer(sec_img, dtype='uint8')

	#reshaping image
	if metadata[0] == 1: # grayscale
		sec_img = np.reshape(sec_img,(sec_img_width,sec_img_height))
	elif metadata[0] == 3:
		sec_img = sec_img = np.reshape(sec_img,sec_img_shape)
	return sec_img


def psnr(cover_img, stego_img):
	mse = np.sum((cover_img - stego_img) ** 2 ) / np.prod(cover_img.shape)
	return 20 * math.log10(255) - 10 * math.log10(mse)

def max_diff(cover_img, stego_img):
	cover_img = cover_img.astype(np.int32)
	stego_img = stego_img.astype(np.int32)
	return np.max(abs(cover_img - stego_img))

def main():

	parser = argparse.ArgumentParser(description = 'Performs Steganography')
	parser.add_argument("coverimage", help="Cover Image path")
	parser.add_argument("secretimage", help="Secret Image path")
	parser.add_argument("key", help="Key to encrypt Secret Image")
	args = parser.parse_args()
	cover_img_path = args.coverimage
	sec_img_path = args.secretimage
	strKey = args.key

	print('Loading ...')
	tick = time.clock()
	#loading
	cover_img = ftools.load_image(cover_img_path)
	sec_img = ftools.load_image(sec_img_path)
	tock = time.clock()
	print('Loading Complete. Time taken ' + str(tock - tick))

	print('Hiding image ...')
	tick = time.clock()
	#hide
	stego_img= hide_image(cover_img, sec_img, strKey)
	ftools.save_image(stego_img,"stego.png")
	tock = time.clock()
	print('Hiding Complete. Time Taken ' + str(tock - tick))
	print ("PSNR is "+ str(psnr(cover_img, stego_img)))
	print ("Max pixel difference is "+ str(max_diff(cover_img, stego_img)))

	print('Retrieving image ...')
	tick = time.clock()
	#unhide
	ext_sec_img = unhide_image(stego_img, strKey)
	ftools.save_image(ext_sec_img, 'ext_sec_img.png')
	tock = time.clock()
	print('Image Retrieved. Time Taken ' + str(tock - tick))


if __name__ == "__main__":
	main()
