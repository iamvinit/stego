import numpy as np
import scipy as sp
from PIL import Image
from scipy.linalg import pascal
import time

# Loads Image and converts it into numpy array
def load_image(path):
	img = Image.open(path)
	img.load()
	data = np.asarray( img, dtype="uint8" )
	return data

# Performs Fast Discrete Pascal Transform on on all the SxS blocks of numpy array 
# See: http://dsmc.eap.gr/pubs/ans-b23.pdf 
def fdpt(img, block_size = 2, shape = 0): 
	if shape == 0:
		shape = img.shape

	if np.prod(img.shape) % block_size != 0:
		raise ValueError("Cannot divide image into blocks of "+ str(block_size))
	
	# dividing into blocks
	img_blocks = np.reshape(img,(-1,block_size)).T

	# performing FDPT
	img_freq_blocks = img_blocks.copy().astype(np.int32)
	for i in range(block_size - 1):
		img_freq_blocks[i+1:] = img_freq_blocks[i:-1] - img_freq_blocks[i+1:]

	return np.reshape(img_freq_blocks.T, shape)

# Performs Inverse Fast Discrete Pascal Transform on on all the SxS blocks of numpy array 
def ifdpt(img_freq, block_size = 2, shape = 0): 
	return fdpt(img_freq, block_size, shape).astype(np.uint8)

# Performs Discrete Pascal Transform using Pascal Transform Matrix
def dpt(img, block_size = 2):
	img_dim = img.shape

	if np.prod(img_dim) % block_size != 0:
		raise ValueError("Cannot divide image into blocks of "+ str(block_size))
	
	# dividing into blocks
	img_blocks = np.reshape(img,(-1,block_size)).T

	# generating pascal transform matrix
	pascal_matrix = pascal(block_size, kind='lower').astype(np.int16)
	pascal_matrix[:,1::2] *= -1

	# performing FDPT
	img_freq_blocks =np.dot(pascal_matrix, img_blocks)

	return np.reshape(img_freq_blocks.T, img_dim)

# Save image from numpy array
def save_image(img, name='output.bmp'):
	img = Image.fromarray(img)
	img.save(name)