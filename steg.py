import sys
import fdpttools as ftools
import triencryptbytes as te
import numpy as np

def hide_image(cover_img, sec_img):

	#encryption
	e_sec_img , key = te.encrypt(bytearray(sec_img))
	e_sec_img = np.frombuffer(e_sec_img, dtype='uint8')
	e_sec_img =  np.repeat(e_sec_img, 4, axis = 0)
	e_sec_img[::4] = e_sec_img[::4] >> 6
	e_sec_img[1::4] = (e_sec_img[1::4] >> 4) & 3
	e_sec_img[2::4] = (e_sec_img[2::4] >> 2) & 3
	e_sec_img[3::4] = e_sec_img[3::4] & 3
	#ftools.save_image(np.reshape(e_sec_img,(512,512)),"encrypted.png")

	e_sec_img.resize(cover_img.shape)

	#hide
	cover_img = cover_img & int('11111100',2)
	stego_img = cover_img | e_sec_img
	ftools.save_image(stego_img,"stego.png")



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
	stego_img = hide_image(cover_img, sec_img)


	# fre_img = ftools.fdpt(img, 4)
	# out = ftools.ifdpt(fre_img, 4)
	# ftools.save_image(fre_img, 'freq.png')
	# ftools.save_image(out, 'output.bmp')

if __name__ == "__main__":
	main()
