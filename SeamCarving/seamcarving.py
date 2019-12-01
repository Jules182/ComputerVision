import numpy as np 
import pandas as pd 
import cv2 # OpenCV Library
import os

def resize_img(img, height, width):
    # resize
    dim = (width, height)
    resized = cv2.resize(img, dim)

    # show image
    # cv2.imshow(f'{width}x{height}', resized)
    # cv2.waitKey(0)

    return resized

if __name__ == '__main__':
    input_dir = "./img/input"
    output_dir = "./img/output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for path, _, files in os.walk(input_dir):
        for file in files:
            file_lc = file.lower()
            if file_lc.endswith(".png") or file_lc.endswith(".jpg") or file_lc.endswith(".jpeg"):
                img_name = os.path.splitext(file)[0]
                # read file
                img = cv2.imread(os.path.join(path, file))
                height, width, channels = img.shape
                # resize
                new_height = int(height / 2)
                new_width = int(width / 2)
                resized = resize_img(img, new_height, new_width)
                # write file
                output_filename = os.path.join(output_dir, f'{img_name}-{new_width}x{new_height}.jpg')
                cv2.imwrite(output_filename, resized)
                print(f'{img_name} ({width}x{height}) exported with new width={new_width} and height={new_height}')