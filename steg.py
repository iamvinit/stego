import sys
import fdpttools as ftools
import triencryptbytes as te
import numpy as np
import base64

# hides 2 bit of cover_img with sec_img
def hide_image(cover_img, sec_img):
	# stego_img becomes negetive  sometimes when 2 bits of cover_img_freq is replaced 
	# To solve this we make cover image lie from 4-251 
	# 
	cover_img = np.copy(cover_img)
	cover_img[ cover_img > 253] = 251
	cover_img[ cover_img < 4] = 4

	#encrypting the sec_img
	e_sec_img , key = te.encrypt(bytearray(sec_img))
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
	cover_img_freq = ftools.fdpt(cover_img)
	#hiding encrypted sec_img in cover_img_freq
	stego_img_freq = ((cover_img_freq >> 2) << 2) | e_sec_img


	# cover_img_freq = np.reshape(cover_img_freq, -1)
	# stego_img_freq = np.ndarray(cover_img_freq.shape, dtype='int32')
	# e_sec_img = np.reshape(e_sec_img, -1)
	# i = 0
	# while i < cover_img_freq.shape[0]:
	# 	stego_img_freq[i] = ((cover_img_freq[i] >> 2) << 2) | e_sec_img[i]
	# 	if ((stego_img_freq[i] >> 2 ) != (cover_img_freq[i] >> 2 )):
	# 		print ("they are not equal")
	# 		print(bin(stego_img_freq[i]))
	# 		print(bin(cover_img_freq[i]))
	# 		break

	# 	i = i + 1


		
	#converting stego_img_freq to spatial domain
	stego_img = ftools.ifdpt(stego_img_freq)

	#error image with noice generated

	# si = np.reshape(stego_img , -1)
	# ci = np.reshape(cover_img, -1)
	# sif = np.reshape(stego_img_freq, -1)
	# cif = np.reshape( cover_img_freq, -1)
	# k = 0
	# for i in np.reshape(stego_img - cover_img, -1)  :
	# 	if abs(i) > 3:
	# 		print ("they are equal asdasd asd asd ")
	# 		print(k)
	# 		print(ci[k])
	# 		print(cif[k])
	# 		print(si[k])
	# 		print(sif[k])
	# 		print(k-1)
	# 		print(ci[k-1])
	# 		print(cif[k-1])
	# 		print(si[k-1])
	# 		print(sif[k-1])
	# 		break
	# 	k = k + 1
	
	ftools.save_image(stego_img,"stego.png")
	return (stego_img,key)

def unhide_image(stego_img, key):
	#extract sec_img
	stego_img = np.reshape(stego_img, (-1,4))
	stego_img = stego_img & 3
	stego_img[:,0]  = (stego_img[:,0] << 6) | (stego_img[:,1] << 4) | (stego_img[:,2] << 2) | stego_img[:,3] 
		
	#decrypt sec_img
	sec_img = te.decrypt(bytearray(stego_img[:,0]), key)
	sec_img = np.frombuffer(sec_img, dtype='uint8')

	#assuming dim is known
	sec_img = np.reshape(sec_img,(256,256))

	ftools.save_image(sec_img, 'ext_sec_img.png')

	return sec_img


def main():
	if len(sys.argv) < 2:
		print("Usage fdpt.py image.png")
		print("Using default image")
		cover_img_path = './Images/boat.512.tiff'
	else:
		cover_img_path = sys.argv[1]

	sec_img_path = './Images/5.1.14.tiff'

	#loading
	cover_img = ftools.load_image(cover_img_path)
	sec_img = ftools.load_image(sec_img_path)

	#hide
	stego_img, key = hide_image(cover_img, sec_img)

	#unhide
	unhide_image(stego_img, key)

	strKey = base64.b64encode(key).decode()
	#print(strKey)

	# fre_img = ftools.fdpt(img, 4)
	# out = ftools.ifdpt(fre_img, 4)
	# ftools.save_image(fre_img, 'freq.png')
	# ftools.save_image(out, 'output.bmp')

if __name__ == "__main__":
	main()
