import cv2
import numpy as np
import sys
import os

symbols_list = ["#", "-", "*", ".", "+", "o"]
threshold_list = [0, 50, 100, 150, 200]


def print_out_ascii(array):
    """prints the coded image with symbols"""
    for row in array:
        for e in row:
            # select symbol based on the type of coding
            print(symbols_list[int(e) % len(symbols_list)], end="")
        print()


def img_to_ascii(image):
    """returns the numeric coded image"""
    height, width = image.shape

    # Simple trick: ensure new dimensions are at least 1 to avoid cv2 errors on tiny images
    new_width = max(1, int(width / 20))
    new_height = max(1, int(height / 40))

    # resize image to fit the printing screen
    resized_image = cv2.resize(image, (new_width, new_height))

    thresh_image = np.zeros(resized_image.shape)

    for i, threshold in enumerate(threshold_list):
        # assign corresponding values according to the index of threshold applied
        thresh_image[resized_image > threshold] = i
    return thresh_image


if __name__ == "__main__":
    # If no argument is provided, default to sample_image.png
    if len(sys.argv) < 2:
        print("Image Path not specified : Using sample_image.png\n")
        image_path = "sample_image.png"
    else:
        print("Using {} as Image Path\n".format(sys.argv[1]))
        image_path = sys.argv[1]

    # Check if file actually exists before passing it to OpenCV
    if not os.path.exists(image_path):
        print(f"Error: Could not find the file at '{image_path}'")
        print("Please make sure the file exists and the path is correct.")
        sys.exit(1)

    image = cv2.imread(image_path, 0)  # read image as grayscale

    # Double check OpenCV successfully loaded it
    if image is None:
        print(f"Error: OpenCV could not read '{image_path}'. It might be corrupted.")
        sys.exit(1)

    ascii_art = img_to_ascii(image)
    print_out_ascii(ascii_art)