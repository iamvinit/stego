from steg import hide_image, psnr, max_diff
import fdpttools as ftools
import argparse
import time

def main(cover_img_path, sec_img_path, strKey, outputfilename):

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
	ftools.save_image(stego_img,outputfilename)
	tock = time.clock()
	print('Hiding Complete. Time Taken ' + str(tock - tick))
	print ("PSNR is "+ str(psnr(cover_img, stego_img)))
	print ("Max pixel difference is "+ str(max_diff(cover_img, stego_img)))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Hides secret image in cover image')
	parser.add_argument("coverimage", help="Cover Image path")
	parser.add_argument("secretimage", help="Secret Image path")
	parser.add_argument("key", help="Key to encrypt Secret Image")
	parser.add_argument("-o", "--outputfilename", help="Output file name")
	args = parser.parse_args()
	cover_img_path = args.coverimage
	sec_img_path = args.secretimage
	strKey = args.key
	if(args.outputfilename):
		outputfilename = args.outputfilename
	else:
		outputfilename = 'stego.png'

	main(cover_img_path, sec_img_path, strKey, outputfilename)