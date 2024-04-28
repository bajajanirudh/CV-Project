import math
from bitarray import bitarray
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys

class Decode :
    MAX_WINDOW_SIZE = 400
    
    def __init__(self, window_size=20):
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE)
        self.lookahead_buffer_size = 15 
  
    def rle_decode(self, rle_data, image_shape):

        reconstructed_image = np.zeros(image_shape, dtype=np.uint8)
        current_index = 0

        for value, run_length in rle_data:
            for _ in range(run_length):
                reconstructed_image.flat[current_index:current_index + 3] = value
                current_index += 3

        return reconstructed_image.reshape(image_shape)

    def Lz77decompress(self, input_file_path, output_file_path=None):
        data = bitarray(endian='big')
        output_buffer = []

        try:
            with open(input_file_path, 'rb') as input_file:
                data.fromfile(input_file)
        except IOError:
            print('Could not open input file ...')
            raise

        while len(data) >= 9:
            flag = data.pop(0)
            if not flag:
                byte = data[0:8].tobytes()
                output_buffer.append(byte)
                del data[0:8]
            else:
                byte1 = ord(data[0:8].tobytes())
                byte2 = ord(data[8:16].tobytes())

                del data[0:16]
                distance = (byte1 << 4) | (byte2 >> 4)
                length = (byte2 & 0xf)

                for i in range(length):
                    output_buffer.append(output_buffer[-distance])
        out_data =  b''.join(output_buffer)

        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(out_data)
                    print('File was decompressed successfully and saved to output path ...')
                    return None
            except IOError:
                print('Could not write to output file path. Please check if the path is correct ...')
                raise
        return out_data

    def findLongestMatch(self, data, current_position):
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data) + 1)
        best_match_distance = -1
        best_match_length = -1
        
        for j in range(current_position + 2, end_of_buffer):
            start_index = max(0, current_position - self.window_size)
            substring = data[current_position:j]
            for i in range(start_index, current_position):
                repetitions = len(substring) // (current_position - i)
                last = len(substring) % (current_position - i)
                matched_string = data[i:current_position] * repetitions + data[i:i+last]
                if matched_string == substring and len(substring) > best_match_length:
                    best_match_distance = current_position - i
                    best_match_length = len(substring)

        if best_match_distance > 0 and best_match_length > 0:
            return (best_match_distance, best_match_length)
        return None 

    def decompress(self, foreground_image_path, background_image_path):
        compressed_foreground = plt.imread(foreground_image_path) 
        foreground_image_shape = (4288, 2848, 4)
        
        read_compress_fore = []
        for i in range(len(compressed_foreground)):
        k,l = compressed_foreground[i][0][:3], compressed_foreground[i][0][3]
        read_compress_fore.append((k,l))
        
        reconstructed_foreground = self.rle_decode(read_compress_fore, foreground_image_shape)
        output_file_path = './files/reconstructed_background.jpg'
        self.decompress(background_image_path, output_file_path)
        
        reconstructed_background = cv2.imread('./files/reconstructed_background.jpg')
        reconstructed_image = reconstructed_foreground + reconstructed_background
        cv2.imwrite('reconstructed_image.jpg', reconstructed_image)
        
        return


if __name__ == "__main__":
    foreground_image_path = sys.argv[1]
    background_image_path = sys.argv[2]
    decoder = Decode()
    decoder.encode(foreground_image_path, background_image_path)

