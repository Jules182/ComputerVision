import numpy as np
import cv2  # OpenCV Library
import os

import matplotlib.pyplot as plt


def grayscale(img):
    """
    Convert a color image to grayscale
    """
    b, g, r = img[:,:,0], img[:,:,1], img[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return np.floor(gray)

def convolution(img, filter):
    """
    Convolution operator
    """
    img_height, img_width = img.shape

    # prevent edges from being the minimum by setting them to 255
    output = np.full((img_height, img_width), 255)

    for row in range(0,img_height-2):
        for col in range(0,img_width-2):
            output[row+1,col+1] = np.sum(filter * img[row:row + 3, col:col + 3])

    return output

def sobel(img):
    """
    Sobel filter in x and y direction to retrieve the magnitude of the edges
    """
    filter_x = np.array([
    [-1, 0, 1], 
    [-2, 0, 2], 
    [-1, 0, 1]
    ])

    filter_y = np.array([
    [-1, -2, -1], 
    [0, 0, 0], 
    [1, 2, 1]
    ])

    new_image_x = convolution(img, filter_x)
    new_image_y = convolution(img, filter_y)

    magnitude = np.abs(new_image_x) +  np.abs(new_image_y)

    return magnitude

def find_seams_vertical(img, energy):
    """
    Find the optimal vertical seam and highlight it on the input image
    Paper: Avidan et al. (2007)
    """
    img_height, img_width = energy.shape

    cumulated_min_energy = energy.copy()
    output = img.copy()

    # compute the cumulative minimum energy M for all possible connected seams
    for row in range(1,img_height):
        for col in range(img_width):
            if col == 0:
                cumulated_min_energy[row, col] = energy[row, col] + min(cumulated_min_energy[row-1, col:col+1])
            elif col == img_width-1:
                cumulated_min_energy[row, col] = energy[row, col] + min(cumulated_min_energy[row-1, col-1:col])
            else:
                cumulated_min_energy[row, col] = energy[row, col] + min(cumulated_min_energy[row-1, col-1:col+1])

    # backtracking to find the path of the optimal seam
    col = np.argmin(cumulated_min_energy[img_height-1,:])
    for row in reversed(range(0,img_height)):
        # insert a 2px wide red stroke to mark the seam
        output[row, col] = [0,0,255]
        if not col > img_width-3:
            output[row,col+1] = [0,0,255]

        if col == 0:
            col = np.argmin(cumulated_min_energy[row-1, col:col+1]) + col
        elif col == img_width-1:
            col = np.argmin(cumulated_min_energy[row-1, col-1:col]) + col-1
        else:
            col = np.argmin(cumulated_min_energy[row-1, col-1:col+1]) + col-1

    return output


def resize_img(img, new_height, new_width):
    """
    Resize an image to a new height x width
    """
    height, width, channels = img.shape
    # resize
    seams_to_remove_x = width - new_width
    seams_to_remove_y = height - new_height

    # convert to grayscale
    gray = grayscale(img)

    # plt.imshow(gray, cmap='gray')
    # plt.title("Gray")
    # plt.show()

    # run sobel operator on the grayscale image
    energy_img = sobel(gray)

    # plt.imshow(energy_img, cmap='gray')
    # plt.title("Energy function Sobel")
    # plt.show()

    # find and mark an optimal seam on the input image
    img_seam = find_seams_vertical(img, energy_img)
    
    cv2.imshow("optimal seam (x)", img_seam)
    cv2.waitKey(0)

    # TODO remove seams from image

    return img_seam

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
                height, width, _ = img.shape
                # resize
                new_height = int(height)
                new_width = int(width - 1)
                print(f'resizing {file} to ({new_width}x{new_height})')
                resized = resize_img(img, new_height, new_width)
                # write file
                output_filename = os.path.join(output_dir, f'{img_name}-{new_width}x{new_height}.png')
                cv2.imwrite(output_filename, resized)
                print(f'{img_name}-{new_width}x{new_height}.png exported')