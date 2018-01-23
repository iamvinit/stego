from steg import unhide_image
import fdpttools as ftools
import argparse
import time

parser = argparse.ArgumentParser(description = 'Extracts secret image From Stego image')
parser.add_argument("stegoimage", help="Stego Image path")
parser.add_argument("key", help="Key to encrypt Secret Image")
parser.add_argument("-o", "--outputfilename", help="Output file name")
args = parser.parse_args()
stego_img_path = args.stegoimage
strKey = args.key
if(args.outputfilename):
	outputfilename = args.outputfilename
else:
	outputfilename = 'ext_sec_img.png'

print('Loading ...')
tick = time.clock()
#loading
stego_img = ftools.load_image(stego_img_path)
tock = time.clock()
print('Loading Complete. Time taken ' + str(tock - tick))

print('Retrieving image ...')
tick = time.clock()
#unhide
ext_sec_img = unhide_image(stego_img, strKey)
ftools.save_image(ext_sec_img, outputfilename)
tock = time.clock()
print('Image Retrieved. Time Taken ' + str(tock - tick))