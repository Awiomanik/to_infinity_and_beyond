# Author Wojciech Kosnik-Kowalczuk WKK
# AntiAliasing tool for fractal renderers (and possibly other things)

# TODO:
# - check parameters for AntiAliasing_from_file function (kernel, kernel_size, kernel_sigma)
# - implement other kernels
# - implement AntiAliasing_from_array (for using in fractal renderers)
# - input validation
# - vectorize convolution for faster performance
# - refactor code into script


# IMPORTS
from PIL import Image
import numpy as np
from loading_bar import LoadingBar as lb


# HELPER FUNCTIONS
def get_gaussian_kernel(size: int = 3, sigma: float = 1.0) -> np.ndarray:
    """
    Returns a symmetric squere Gaussian kernel of size size, 
    with the provided sigma value.

    Gaussian 2D kernel is defined as:
    g(x, y) = exp(-(x**2 + y**2) / (2 * sigma**2)) / (2 * pi * sigma**2)
    """

    # initialize grid
    x, y = np.meshgrid(np.linspace(-size/2, size/2, size), np.linspace(-size/2, size/2, size))

    # calculate kernel values
    kernel = np.exp(-(x**2 + y**2) / (2 * sigma**2)) / (2 * np.pi * sigma**2) 

    # normalize kernel
    kernel = kernel / np.sum(kernel)

    return kernel


# MAIN ANTI-ALIASING FUNCTIONS
# TODO:
# - implement other kernels
# - vectorize convolution for faster performance
def AntiAliasing_from_file(path:str, kernel_type:str="gaussian", kernel_size:int=3, kernel_sigma:float=1.0):


    # get the image 
    img = Image.open(path)

    # cast image to numpy array
    img_arr = np.array(img)

    # define karnel
    if kernel_type == "gaussian":
        kernel = get_gaussian_kernel(kernel_size, kernel_sigma)

    # get image dimensions
    height, width, channels = img_arr.shape

    # initialize new image array (reduce size by kernel_size)
    new_img_arr = np.zeros((height // kernel_size, width // kernel_size, channels), dtype=img_arr.dtype)

    # initialize loading bar
    lb1 = lb(height)

    # convolve image with kernel
    for i in range(0, height, kernel_size):
        for j in range(0, width, kernel_size):
            for k in range(channels):

                # convolve kernel with image
                new_pixel = 0
                for l in range(kernel_size):
                    for m in range(kernel_size):
                        new_pixel += img_arr[i+l][j+m][k] * kernel[l][m]

                # update new image array
                new_img_arr[i//kernel_size][j//kernel_size][k] = new_pixel

        # update loading bar        
        lb1.update(i+1, skip_every_other=20)

    # cast back to image
    img = Image.fromarray(new_img_arr)

    # save image
    new_path = path[:path.rfind('.')] + "_aa_" + str(kernel_type) + '_' + str(kernel_size) + 'x' + str(kernel_size) + '_' + str(kernel_sigma) + ".png"
    img.save(new_path)

    # close loading bar
    lb1.close(additional_info="Image saved as: " + new_path)
    

# TESTING
# TODO:
# - check parameters for AntiAliasing_from_file function (kernel, kernel_size, kernel_sigma)
if __name__ == "__main__":

    file_name = "renders_aa/test_nipy_spectral.png"
    AntiAliasing_from_file(file_name, kernel_size=2, kernel_sigma=1.0)
