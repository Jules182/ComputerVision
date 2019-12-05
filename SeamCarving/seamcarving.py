import numpy as np
import cv2  # OpenCV Library
import os
import argparse,sys

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

def remove_seam_vertical(img, energy):
    """
    Find the optimal vertical seam and remove it
    Paper: Avidan et al. (2007)
    """
    img_height, img_width = energy.shape

    cumulated_min_energy = energy.copy()
    output_img = np.zeros((img_height, img_width - 1, 3))
    output_energy = np.zeros((img_height, img_width - 1))

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
    for row in reversed(range(img_height-1)):

        # remove the seam in the output and the energy image
        output_img[row,:] = np.delete(img[row,:], col, 0)
        output_energy[row,:] = np.delete(energy[row,:], col, 0)

        if col == 0:
            col = np.argmin(cumulated_min_energy[row-1, col:col+1]) + col
        elif col == img_width-1:
            col = np.argmin(cumulated_min_energy[row-1, col-1:col]) + col-1
        else:
            col = np.argmin(cumulated_min_energy[row-1, col-1:col+1]) + col-1

    return (output_img, output_energy)

def resize_img(img, seams_to_remove_x, seams_to_remove_y):
    """
    Resize an image to a new height and width by removing low-energy-pixels (seams)
    """
    # convert to grayscale
    gray = grayscale(img)

    # run sobel operator on the grayscale image
    energy_img = sobel(gray)

    # remove the specified number of vertical seams from the image
    for i in range(seams_to_remove_x):
        img, energy_img = remove_seam_vertical(img, energy_img)

    # rotate the image to remove horizontal seams
    img_hor = np.rot90(img)
    energy_img_hor = np.rot90(energy_img)
    
    # remove the specified number of horizontal seams from the image
    for j in range(seams_to_remove_y):
        img_hor, energy_img_hor = remove_seam_vertical(img_hor, energy_img_hor)
    
    # rotate the image back
    img = np.rot90(img_hor)
    img = np.rot90(img)
    img = np.rot90(img)
    energy_img = np.flip(energy_img_hor)
    energy_img = np.flip(energy_img)
    energy_img = np.flip(energy_img)

    return img

if __name__ == '__main__':
    input_dir = "./img/input"
    output_dir = "./img/output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the seams to remove in x- and y-direction
    # from the command line arguments "-x" and "-y"
    parser=argparse.ArgumentParser()
    parser.add_argument('-x', type=int, help='Number of vertical seams to remove')
    parser.add_argument('-y', type=int, help='Number of horizontal seams to remove')
    args=parser.parse_args()

    if args.x is None and args.y is None:
        sys.exit(0)

    seams_to_remove_x = args.x
    seams_to_remove_y = args.y

    if args.x is None:
        seams_to_remove_x = 0
    
    if args.y is None:
        seams_to_remove_y = 0

    # rezize every image in the input directory
    for path, _, files in os.walk(input_dir):
        for file in files:
            file_lc = file.lower()
            if file_lc.endswith(".png") or file_lc.endswith(".jpg") or file_lc.endswith(".jpeg"):
                img_name = os.path.splitext(file)[0]
                # read file
                img = cv2.imread(os.path.join(path, file))
                height, width, _ = img.shape
                new_height = int(height - seams_to_remove_y)
                new_width = int(width - seams_to_remove_x)
                if new_width >= 1 and new_height >= 1:
                    print(f'resizing {file} to ({new_width}x{new_height})')
                    # resize
                    resized = resize_img(img, seams_to_remove_x, seams_to_remove_y)
                    # write file
                    output_filename = os.path.join(output_dir, f'{img_name}-{new_width}x{new_height}.png')
                    cv2.imwrite(output_filename, resized)
                    print(f'{img_name}-{new_width}x{new_height}.png exported')