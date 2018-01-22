import sys
import fdpttools as ftools
import triencryptbytes as te
import numpy as np
import math
import argparse
block_size = 2

# hides 2 bit of cover_img with sec_img
def hide_image(cover_img, sec_img, strKey):
	# stego_img becomes negetive  sometimes when 2 bits of cover_img_freq is replaced 
	# To solve this we make cover image lie from 4-251 
	cover_img = np.copy(cover_img)
	#cover_img[ cover_img > 251] = 251
	cover_img[ cover_img < 4] = 4

	#encrypting the sec_img
	e_sec_img = te.encrypt(bytearray(sec_img), strKey)
	e_sec_img = np.frombuffer(e_sec_img, dtype='uint8')

	#converting encrypted sec_img to same dimension as cover_img
	e_sec_img =  np.repeat(e_sec_img, 4, axis = 0)
	e_sec_img[::4] = e_sec_img[::4] >> 6
	e_sec_img[1::4] = (e_sec_img[1::4] >> 4) & 3
	e_sec_img[2::4] = (e_sec_img[2::4] >> 2) & 3
	e_sec_img[3::4] = e_sec_img[3::4] & 3
	#ftools.save_image(np.reshape(e_sec_img,(512,512)),"encrypted.png")
	e_sec_img.resize(cover_img.shape)

	#converting cover_img to frequency domain
	cover_img_freq = ftools.fdpt(cover_img,block_size)
	#hiding encrypted sec_img in cover_img_freq
	stego_img_freq = ((cover_img_freq >> 2) << 2) | e_sec_img
	
	#converting stego_img_freq to spatial domain
	stego_img = ftools.ifdpt(stego_img_freq,block_size)

	return stego_img

def unhide_image(stego_img, strKey):

	#converting stego_img to frequency domain
	stego_img_freq = ftools.fdpt(stego_img,block_size)

	#extract sec_img
	stego_img_freq = (np.reshape(stego_img_freq, (-1,4)) & 0b11).astype(np.uint8)
	stego_img_freq[:,0]  = (stego_img_freq[:,0] << 6) | (stego_img_freq[:,1] << 4) | (stego_img_freq[:,2] << 2) | stego_img_freq[:,3] 

	#decrypt sec_img
	sec_img = te.decrypt(bytearray(stego_img_freq[:256*256,0]), strKey)
	sec_img = np.frombuffer(sec_img, dtype='uint8')

	#assuming dim is known
	sec_img = np.reshape(sec_img,(256,256))
	
	return sec_img


def psnr(cover_img, stego_img):
	mse = np.sum((cover_img - stego_img) ** 2 ) / np.prod(cover_img.shape)
	return 20 * math.log10(255) - 10 * math.log10(mse)

def max_diff(cover_img, stego_img):
	cover_img = cover_img.astype(np.int32)
	stego_img = stego_img.astype(np.int32)
	return np.max(abs(cover_img - stego_img))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("coverimage", help="Cover Image path")
	parser.add_argument("secretimage", help="Secret Image path")
	parser.add_argument("key", help="key to encrypt Secret Image")
	args = parser.parse_args()
	cover_img_path = args.coverimage
	print(cover_img_path)



	# if len(sys.argv) < 2:
	# 	print("Usage fdpt.py image.png")
	# 	print("Using default image")
	# 	cover_img_path = './Images/boat.512.tiff'
	# else:
	# 	cover_img_path = sys.argv[1]


	sec_img_path = './Images/5.1.14.tiff'
	strKey = 'qwerty'

	#loading
	cover_img = ftools.load_image(cover_img_path)
	sec_img = ftools.load_image(sec_img_path)

	#hide
	stego_img= hide_image(cover_img, sec_img, strKey)

	ftools.save_image(stego_img,"stego.png")

	print ("psnr is "+ str(psnr(cover_img, stego_img)))
	print ("max pixel diff is "+ str(max_diff(cover_img, stego_img)))
	#unhide
	unhide_image(stego_img, strKey)

	ftools.save_image(sec_img, 'ext_sec_img.png')

	#strKey = base64.b64encode(key).decode()
	#print(strKey)

	# fre_img = ftools.fdpt(img, 4)
	# out = ftools.ifdpt(fre_img, 4)
	# ftools.save_image(fre_img, 'freq.png')
	# ftools.save_image(out, 'output.bmp')

if __name__ == "__main__":
	main()
