# CV-Project
Image compression on HDR images with separate filters on background and forground


# To run code : .ipynb

upload the image file 
change the image file name in the 3rd output cell
and rull all cells.

output images "compressed_foreground.png" and "compressed_background.jpg" will be generated, can be used for comparing data size.
the reconstructed image "reconstructed_image.jpg" can be viewed for comparision of data loss.
all other images are residual for code running purpose and can be ignored.

# For using the .py files

## For Compressing
open terminal 
    python image_compressor.py "input_image_path"

"compressed_background.png" and "compressed_background.jpg" will be generated

## For Decompressing 
open terminal
    python decompressor.py "compressed_foreground" "compressed_background"

"reconstructed_image.jpg" will be obtained.
