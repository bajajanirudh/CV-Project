import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
from skimage import io, color, segmentation
from skimage.future import graph
from scipy import ndimage as ndi
from rembg import remove
import math
from bitarray import bitarray
import sys

class Encode :
    MAX_WINDOW_SIZE = 400
    
    def __init__(self, window_size=20):
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE)
        self.lookahead_buffer_size = 15 # length of match is at most 4 bits

    def rle_encode(self, image):
        flattened_image = image.flatten()
        rle_data = []
        current_value = flattened_image[:3]  # Initialize with the first pixel RGB values
        run_length = 1

        for i in range(3, len(flattened_image), 3):
            pixel = flattened_image[i:i+3]
            if np.array_equal(pixel, current_value):
                run_length += 1
            else:
                rle_data.append((current_value, run_length))
                current_value = pixel
                run_length = 1

        rle_data.append((current_value, run_length))

        for i in range(len(rle_data)):
            k,l = rle_data[i]
            rle_data[i] = np.append(rle_data[i][0], l)
            
        rle_data = np.array(rle_data)
        plt.imsave("compressed_foreground.png", rle_data)
        return 
    
    def Lz77compress(self, input_file_path, output_file_path=None, verbose=False):
        data = None
        i = 0
        output_buffer = bitarray(endian='big')

        try:
            with open(input_file_path, 'rb') as input_file:
                data = input_file.read()
        except IOError:
            print('Could not open input file ...')
            raise
        
        while i < len(data):
            match = self.findLongestMatch(data, i)
            
            if match:
                (bestMatchDistance, bestMatchLength) = match

                output_buffer.append(True)
                output_buffer.frombytes(bytes([bestMatchDistance >> 4]))
                output_buffer.frombytes(bytes([((bestMatchDistance & 0xf) << 4) | bestMatchLength]))

                if verbose:
                    print("<1, %i, %i>" % (bestMatchDistance, bestMatchLength), end='')
                
                i += bestMatchLength
            
            else:
                output_buffer.append(False)
                output_buffer.frombytes(bytes([data[i]]))

                if verbose:
                    print("<0, %s>" % data[i], end='')

                i += 1

        output_buffer.fill()

        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(output_buffer.tobytes())
                    print("File was compressed successfully and saved to output path ...")
                    return None
            except IOError:
                print('Could not write to output file path. Please check if the path is correct ...')
                raise
        
        return output_buffer


    def encode(self, image_path):
        img = cv2.imread(image_path)
        foreground = remove(img)
        foreground_image = foreground[:, :, :3]
        background_image = img - foreground_image
        
        cv2.imwrite('./files/background.jpg', background_image)
        input_file_path = './files/background.jpg'
        output_file_path = 'compressed_background.jpg'
        
        self.rle_encode(foreground_image)
        self.LZ77Compressor(input_file_path, output_file_path)
        


def main(args):
    print("Arguments passed:", args)

if __name__ == "__main__":
    image_path = sys.argv[2]
    encoder = Encode()
    encoder.encode(image_path)
