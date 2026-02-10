import re                                       # regular expressions (file name string creation)
import os                                       # path 
import math                                     # sqrt
import pathlib                                  # path
import time                                     # measuring time of rendering
import numpy as np                              # array manipulation
from PIL import Image                           # image manipulation
from functools import reduce                    # file name string creation
import matplotlib.pyplot as plt                 # colormaps
from PIL import PngImagePlugin as pip           # image metadata
from sympy import sympify, lambdify, symbols    # sympy expression for atractor
from Src.Utils.loading_bar import LoadingBar    # Loading bar for rendering progress

__all__ = ["Julia2png", "Julia2gif"]

# PARENT CLASS FOR RENDERING JULIA SETS
class JuliaSetRenderer:
    '''
    Parent class for rendering Julia sets
    
    Attributes:
    - atractor: atractor function (str)
    - atractor_lambda: atractor function (python function)
    - const, a, b, c: variables for atractor function (complex)
      const - constant complex number
      a, b, c - additional complex numbers 

    - maps: list of mapping functions (list of str)
      use str names of mapping functions to choose them
      for mapping functions that require additional parameters use strings
      separated with ' ' (e.g. "plt BuGn" for matplotlib colormap with BuGn parameter)
      available mapping functions:
        - root (slow to fast)
        - plt # (matplotlib colormap)
        - pltd # (matplotlib colormap and it's reversed version and returns darker pixel for each pixel)
        - rev (reverses orbit)
        - cut # (cuts off orbits below cut_off value)

    - res_w: resolution width (int)
    - res_h: resolution height (int)

    - re_min: minimum real part of complex number (float)
    - re_max: maximum real part of complex number (float)
    - im_min: minimum imaginary part of complex number (float)
    - im_max: maximum imaginary part of complex number (float)

    - max_iter: maximum amount of iterations (int)
    - max_mag: maximum magnitude of complex number (float)

    - target_directory: directory to save renders (str)

    
    Methods:
    - Constructor (__init__)
    - update_parameters (updates parameters)

    - Helper functions:
        - pixel2complex (maps screen coordinates into complex plane)
        - if_in_julia_set (calculates if Julia set contains a given point)
        - if_in_julia_set_vectorized (calculates if Julia set contains a given point (vectorized version))
        - render_color_mapping (maps orbits to colors)

    - Mapping functions:
        - map_slow2fast (maps orbit with sqere root function (slow to fast))
        - map_plt (maps orbit with matplotlib colormap)
        - map_plt_darker (maps orbit with matplotlib colormap and it's reversed version and returns darker pixel for each pixel)
        - map_reverse (reverses orbit)
        
    - Functions to override:
        - file_path 
        - render 
    '''

    # CONSTRUCTOR
    def __init__(self, atractor:str="z^2 + const", \
                 const:complex=0+0j, \
                 a:complex=None, b:complex=None, c:complex=None, \
                 maps:list=["slow_to_fast"], \
                 resolution_w:int=1000, resolution_h:int=1000, \
                 range:tuple=(-2,2,-2,2), \
                 max_ieration:int=256, max_magnitude:float=2, \
                 target_directory:str='') -> None:
        '''
        Constructor
        
        Parameters:
        - atractor: atractor function (str) (default: "z^2 + const")

        - const, a, b, c: variables for atractor function (complex)
            const - constant complex number
            a, b, c - additional complex numbers

        - maps: list of mapping functions (list of str) (default: ["slow_to_fast"])
            use str names of mapping functions to choose them
            for mapping functions that require additional parameters use strings
            separated with ' ' (e.g. "plt BuGn" for matplotlib colormap with BuGn parameter)
            available mapping functions:
                - root (slow to fast)
                - plt # (matplotlib colormap)
                - pltd # (matplotlib colormap and it's reversed version and returns darker pixel for each pixel)
                - rev (reverses orbit)
                - cut # (cuts off orbits below cut_off value)

        - resolution_w: resolution width (int) (default: 1000)
        - resolution_h: resolution height (int) (default: 1000)

        - range: range of complex numbers (tuple) (default: (-2,2,-2,2))
            (im_min, im_max, re_min, re_max)

        - max_ieration: maximum amount of iterations (int) (default: 256)
        - max_mag: maximum magnitude of complex number (float) (default: 2)
        '''

        # initialize atractor
        self.atractor = atractor
        self.const, self.a, self.b, self.c = const, a, b, c

        # evaluate atractor function and symbols
        # define symbols
        complex_symbols = symbols('z const a b c')

        # evaluate atractor function to sympy expression
        atractor_sym_lam = lambdify(complex_symbols, sympify(self.atractor), 'numpy')

        # evaluate atractor function to python function
        self.atractor_lambda = lambda x1, x2, x3, x4, x5: atractor_sym_lam(x1, x2, x3, x4, x5)

        # initialize rest of atributes
        self.maps = maps

        self.res_w = resolution_w
        self.res_h = resolution_h

        self.re_min = range[0]
        self.re_max = range[1]
        self.im_min = range[2]
        self.im_max = range[3]

        self.max_iter = max_ieration
        self.max_mag = max_magnitude

        self.target_directory = target_directory

    # updates given parameters
    def update_parameters(self, atractor:str=None, \
                          const:complex=None, \
                          a:complex=None, b:complex=None, c:complex=None, \
                          resolution_w:int=None, resolution_h:int=None, \
                          range:tuple=None, \
                          max_ieration:int=None, max_magnitude:float=None, \
                          target_directory:str=None) -> None:
        '''Updates given parameters'''

        # update atributes
        if atractor:
            self.atractor = atractor
            self.atractor_expr = sympify(self.atractor)

        if const: self.const = const
        if a: self.a = a
        if b: self.b = b
        if c: self.c = c

        if resolution_w: self.res_w = resolution_w
        if resolution_h: self.res_h = resolution_h

        if range:
            self.re_min = range[0]
            self.re_max = range[1]
            self.im_min = range[2]
            self.im_max = range[3]

        if max_ieration: self.max_iter = max_ieration
        if max_magnitude: self.max_mag = max_magnitude

        if target_directory: self.target_directory = target_directory


    # HELPER FUNCTIONS
    # Maps screen coordinates into complex plane
    def pixel2complex(self, x:int, y:int) -> complex:
        '''Maps screen coordinates (pixels) into complex plane (complex numbers)'''
        return complex(self.re_min + x/self.res_w * (self.re_max - self.re_min), self.im_min + y/self.res_h * (self.im_max - self.im_min))

    # Calculates if Julia set contains a given point
    def if_in_julia_set(self, curr_z:complex=0+0j) -> int:
        '''
        Calculates if Julia set contains a given point. 
        Uses sympy expression for atractor function.

        Returns:
        - amount of iterations till exceeding max_magnitude or max_ieration if not exceeded
        '''

        # iterate till exceeding max_magnitude or max_ieration if not exceeded
        for n in range(self.max_iter):
            
            # evaluate atractor function
            curr_z = self.atractor_lambda(curr_z, self.const, self.a, self.b, self.c)
            if abs(curr_z) > self.max_mag:
                return n
            
        return self.max_iter-1

    # Calculates if Julia set contains a given point (vectorized version)
    def if_in_julia_set_vectorized(self, z_arr:np.array, data:np.array) -> None:
        '''
        Calculates if Julia set contains a given point.
        Uses sympy expression for atractor function.
        
        Vectorized version of if_in_julia_set function,
        might give slightly different results due to linearization of complex numbers.
        Operates on passed data array !!!

        Parameters:
        - z_arr: array of complex numbers corresponding to pixels (np.array)
        - data: array to populate with iterations till exceeding max_magnitude or max_ieration if not exceeded (np.array)
        '''

        # initialize helper arrays
        not_exceeding = np.ones_like(data, dtype=bool) 

        # iterate till exceeding max_magnitude or max_ieration if not exceeded
        for _ in np.arange(self.max_iter):

            # evaluate atractor function for relevant pixels, for current iteration
            z_arr = np.where(not_exceeding, self.atractor_lambda(z_arr, self.const, self.a, self.b, self.c), z_arr)

            # mark points exceeding max_magnitude
            not_exceeding = ~(np.abs(z_arr) > self.max_mag)

            # update data
            data[not_exceeding] += 1

        # shift largest elements to not exceed uint8 range
        data[data == self.max_iter] = self.max_iter-1

    # Distributes points in a way that there are less dense points in the middle and more dense on the edges
    # TODO:
    # - vectorize
    # - check for odd numbers
    # - test for different parameters
    def dense2less_dense2dense_distribiuion(start:complex=0+0j, end:complex=0+1j, amount:int=10, sigma:int=10) -> np.array:
        '''
        Returns array of points with less dense points in the middle and more dense on the edges.
        Uses logarihtmic distribution of points with parameter sigma being the base of logarihtm.

        Parameters:
        - start: start of distribution (float) (default: 0)
        - end: end of distribution (float) (default: 1)
        - amount: amount of points (int) (default: 10)
        - sigma: parameter of logarihtm (int) (default: 10)
        '''

        left = np.logspace(0, 1, amount//2, base=sigma)
        right = np.logspace(1, 0, amount//2, base=sigma)

        re = np.concatenate([left, right])

        re = im = re / re.sum() * (end.real - start.real)


        re[0] = start.real
        im[0] = start.imag

        for i in range(1, len(re)):
            re[i] += re[i-1]
            im[i] += im[i-1]

        return complex(re, im)



    # TODO:
    # - finnish
    def if_in_mandelbrot_set(self, z_arr:np.array, data:np.array) -> None:

        # initialize helper arrays
        not_exceeding = np.ones_like(data, dtype=bool) 
        curr_arr = np.zeros_like(data, dtype=complex)

        # iterate till exceeding max_magnitude or max_ieration if not exceeded
        for _ in np.arange(self.max_iter):

            # evaluate atractor function for relevant pixels, for current iteration
            curr_arr = np.where(not_exceeding, self.atractor_lambda(curr_arr, z_arr , self.a, self.b, self.c), curr_arr)

            # mark points exceeding max_magnitude
            not_exceeding = ~(np.abs(curr_arr) > self.max_mag)

            # update data
            data[not_exceeding] += 1

        data[data == self.max_iter] = self.max_iter-1        

    # Maps orbits to colors
    # TODO: 
    # - put prints outside of function
    def render_color_mapping(self, data:np.array) -> np.array:
        '''Maps orbits to colors'''

        #print("mapping orbits to colors...", end="")

        for map in self.maps:
            # slow to fast
            if map == "root": 
                data = self.map_slow2fast(data)

            # matplotlib colormap
            elif map[:4] == "plt ": 
                data = self.map_plt(data, map[4:])

            # matplotlib colormap and it's reversed version and returns darker pixel for each pixel
            elif map[:4] == "pltd": 
                data = self.map_plt_darker(data, map[5:])

            # reverse orbits values
            elif map == "rev": 
                data = self.map_reverse(data)

            # cut off orbits below cut_off
            elif map[:3] == "cut": 
                data = self.map_cut_off(data, int(map[4:]))

            elif map[:3] == "mod":
                data = self.map_mod(data, int(map[4:]))

            elif map[:3] == "add":
                data = self.map_add(data, int(map[4:]))

            elif map[:3] == "b&w":
                data = self.map_plt_black_white_efficient(data, map[4:])

            else :
                print(f"Mapping function {map} not found")

        #print("\rmapping orbits to colors        DONE")

        return data
    

    # MAPPING FUNCTIONS
    def map_slow2fast(self, orbits:np.array) -> np.array:
        '''Maps orbits array with sqere root function (slow to fast)'''
        return np.vectorize(lambda x: int(math.sqrt(x / self.max_iter) * self.max_iter))(orbits)

    # TODO: describe
    def map_mod(self, orbits:np.array, modulo:int=10) -> np.array:

        return orbits % modulo
    def map_add(self, orbits:np.array, add:int=10) -> np.array:
        return orbits + add

    def map_plt(self, orbits:np.array, map:str="twilight_shifted") -> np.array:
        '''Maps orbits with matplotlib colormap'''

        # normalize orbits
        normalized_orbits = orbits / self.max_iter

        # get colormap
        cmap = plt.colormaps[map]

        # map orbits
        return (cmap(normalized_orbits)[:,:,:3] * self.max_iter).astype(np.uint8) # remove alpha channel
    
    def map_plt_darker(self, orbits:np.array, map:str="twilight_shifted") -> np.array:
        '''Maps orbits with matplotlib colormap and it's reversed version and returns darker pixel for each pixel'''

        # normalize orbits
        normalized_orbits = orbits / self.max_iter

        # get colormap
        cmap = plt.colormaps[map[:-2]] if map[:-2] == "_r" else plt.colormaps[map]
        cmap = plt.colormaps[map]
        cmapr = plt.colormaps[map + "_r"]

        # map orbits
        (cmapr(normalized_orbits)[:,:,:3] * self.max_iter).astype(np.uint8) # remove alpha channel
        (cmap(normalized_orbits)[:,:,:3] * self.max_iter).astype(np.uint8) # remove alpha channel

        return np.array([cmapr(normalized_orbits)[:,:,:3] * self.max_iter, \
                         cmap(normalized_orbits)[:,:,:3] * self.max_iter]).min(axis=0).astype(np.uint8) # remove alpha channel

    def map_reverse(self, orbits:np.array) -> np.array:
        '''Reverses orbits'''
        return self.max_iter - orbits

    def map_cut_off(self, orbits:np.array, cut_off:int=0) -> np.array:
        '''Cuts off orbits below cut_off'''
        return np.vectorize(lambda x: x if x >= cut_off else 0)(orbits)


    # FUNCTIONS TO OVERRIDE
    def file_path(): pass
    def render(): pass

# RENDERING JULIA SETS INTO .PNG FILES
class Julia2png(JuliaSetRenderer):
    '''
    Renders Julia set into .png file
        
    Overwritten methods:
    - Constructor (__init__) (additional attributes: target_directory (str) (default: "renders_png"))
    - file_path (returns file name for given parameters)

    - prepare_metadata (prepares metadata for .png file)
    - render_vectorwise (renders Julia set as numpy array using vectorized render mode)
    - render_pixelwise (renders Julia set as numpy array using pixelwise render mode)
    - print_histogram (prints "histogram" of orbits)

    - render (renders Julia set into .png file)
    '''

    # CONSTRUCTOR
    def __init__(self, atractor:str="z^2 + c", \
                 const:complex=0+0j, \
                 a:complex=0+0j, b:complex=0+0j, c:complex=0+0j, \
                 maps:list=["slow_to_fast"], \
                 resolution_w:int=1000, resolution_h:int=1000, \
                 range:tuple=(-2,2,-2,2), \
                 max_ieration:int=256, max_magnitude:float=2, \
                 target_directory:str="renders_png") -> None:
        '''Constructor''' 

        # initialize parent constructor with changed default target_directory
        super().__init__(atractor, const, a, b, c, maps, \
                         resolution_w, resolution_h, \
                         range, max_ieration, max_magnitude, \
                         target_directory)

        
    # returns file name for given directory
    def file_path(self) -> os.path:
        '''
        Returns file name for given directory:
        julia_atractor_const_a_b_c_resolution_range_max_iterations_max_magnitude_mappings.png
        '''
        # characters forbidden in file names
        forbidden_chars = re.compile(r'[~\\/:"*?<>|] ')

        # return file name with given parameters and forbidden characters replaced with '_'
        #return os.path.join(self.target_directory, re.sub(forbidden_chars,'_', \
        return os.path.join(re.sub(forbidden_chars,'_', \
                            "julia_" + self.atractor + \
                            "_c=" + str(self.const) + \
                            (("_a=" + str(self.a)) if self.a else "") + \
                            (("_b=" + str(self.b)) if self.b else "") + \
                            (("_c=" + str(self.c)) if self.c else "") + \
                            "_res_" + str(self.res_w) + 'x' + str(self.res_h) + \
                            "_ran_" + str(self.re_min) + '_' + str(self.re_max) + \
                                '_' + str(self.im_min) + '_' + str(self.im_max) + \
                            "_iter_" + str(self.max_iter) + \
                            "_mag_" + str(self.max_mag) + \
                            "_map_" + reduce(lambda x, y: x + "_" + y, self.maps) + \
                            ".png"))

    # prepares metadata for .png file
    def prepare_metadata(self) -> pip.PngInfo:
        '''Prepares metadata for .png file'''
        # create metadata
        metadata = pip.PngInfo()
        metadata.add_text("ATRACTOR", str(self.atractor), \
                          ", const=" + str(self.const) + \
                          ", a=" + str(self.a) + ", b=" + str(self.b) + ", c=" + str(self.c))
        metadata.add_text('RESOLUTION', str(self.res_w)+ 'x' + str(self.res_h))
        metadata.add_text('RANGE', str(self.im_min) + ' ' + str(self.im_max) + ' ' + str(self.re_min) + ' ' + str(self.re_max))
        metadata.add_text('MAX_ITERATIONS', str(self.max_iter))
        metadata.add_text('MAX_MAGNITUDE', str(self.max_mag))
        metadata.add_text('MAPPING', reduce(lambda x, y: x + "_" + y, self.maps))

        return metadata

    # renders Julia set into as numpy array using pixelwise render mode
    # TODO:
    # - add mandelbrot functionallity
    def render_vectorwise(self, data:np.array) -> np.array:
        '''Renders Julia set as numpy array using vectorized render mode'''

        print("calculating orbits (vectorwise)...", end="", flush=True)
        start = time.time()

        # initialize array of complex numbers corresponding to pixels
        # np.linspace creates array of evenly spaced numbers over resoluton range
        # np.newaxis adds new axis (column vector) to array
        # data contains complex numbers corresponding to pixels
        z_arr = np.linspace(self.re_min, self.re_max, self.res_w) + 1j \
              * np.linspace(self.im_min, self.im_max, self.res_h)[:, np.newaxis]
        
        # calculate orbits
        self.if_in_julia_set_vectorized(z_arr, data)
        #self.if_in_mandelbrot_set(z_arr, data)

        print("\rcalculating orbits (vectorwise) DONE " + \
                f"(time: {time.time() - start:.2f}s)")
        
    # renders Julia set into as numpy array using pixelwise render mode
    def render_pixelwise(self, data:np.array) -> np.array:
        '''Renders Julia set as numpy array using pixelwise render mode'''

        # initialize loading bar
        lb = LoadingBar(self.res_h)

        # loop through pixels
        for im in range(self.res_h):
            for re in range(self.res_w):

                # calculate orbit
                z = self.pixel2complex(re, im)
                orbit = self.if_in_julia_set(z)

                # update data
                data[im, re] = orbit

            # update loading bar
            lb.update(iteration=im + 1, additional_info="atractor: " + self.atractor, skip_every_other=50)

        # close loading bar
        print(f"\033[Fcalculating orbits (pixelwise)  DONE (time: {lb.close(display_statement=False):.2f}s)") 

    # prints "histogram" of orbits
    def print_histogram(self, data:np.array) -> None:
        '''Prints "histogram" of orbits'''
        # calculate orbits histogram
        orbits = dict(zip(*np.unique(data, return_counts=True)))

        # print orbits histogram
        print()
        print("Orbits count: " + str(len(orbits)))
        print()
        print("Orbits histogram:")
        sorted_orbits = sorted(orbits.items())
        for item in sorted_orbits:
            print(str(item[0]) + ": " + str(item[1]))
        print()

    # renders Julia set into .png file
    def render(self, vectorize_render:bool=False, display_orbits_histogram=False) -> None:
        '''
        Renders Julia set into .png file
        
        Parameters:
        - vectorize_render: if True uses vectorized render,
                            but does not display loading bar
                            (bool) (default: False)
          
        - display_orbits_histogram: if True displays orbits histogram in console
                                    (bool) (default: False)
        '''

        print("initializing...", end="")
        # initialize image
        image = Image.new('RGB', (self.res_h, self.res_w))
        # create metadata:
        metadata = self.prepare_metadata()
        # initialize data
        data = np.zeros((self.res_h, self.res_w), dtype=np.uint8)
        print("\rinitializing                     DONE")

        # create data:
        # vectorwise render mode
        if vectorize_render: self.render_vectorwise(data)
        # pixelwise render mode
        else: self.render_pixelwise(data)

        # map data to colors
        pixels = self.render_color_mapping(data)

        # save data to image
        print("saving image...", end="")
        image = Image.fromarray(pixels, 'RGB')
        pth = pathlib.Path() / "Src" / "Renders" / "renders_png" / self.file_path()
        image.save(pth, pnginfo=metadata)
        print("\rsaving image                    DONE")
        print("\nPicture rendered, you can find it in " + str(pth), end="\n")

        # print "histogram" of orbits
        if display_orbits_histogram:
            self.print_histogram(data)
        
# RENDERING JULIA SETS INTO .GIF FILES
class Julia2gif(JuliaSetRenderer):
    '''
    Renders Julia set into .gif file
    
    Overwritten methods:
    - Constructor (__init__) (additional attributes: target_directory (str) (default: "renders_gif"))
    - file_path (returns file name for given parameters)

    - render_frame (renders Julia set as Image)
    - render (concatanates frames into .gif file)
    '''

    # CONSTRUCTOR
    def __init__(self, atractor:str="z^2 + c", \
                 const:complex=0+0j, \
                 a:complex=0+0j, b:complex=0+0j, c:complex=0+0j, \
                 maps:list=["slow_to_fast"], \
                 resolution_w:int=1000, resolution_h:int=1000, \
                 range:tuple=(-2,2,-2,2), \
                 max_ieration:int=256, max_magnitude:float=2, \
                    target_directory:str="renders_gif") -> None:
        '''Constructor''' 

        # initialize parent constructor with changed default target_directory
        super().__init__(atractor, const, a, b, c, maps, \
                         resolution_w, resolution_h, \
                         range, max_ieration, max_magnitude, \
                         target_directory)

        # initialize target directory
        self.target_directory = target_directory
        

    # returns file name for given directory
    # TODO:
    # - dodaj mozliwosc wlasnej nazwy pliku
    # - skonfiguruj zmienne
    def file_path(self) -> os.path:
        '''
        Returns file name for given directory:
        julia_atractor_const_a_b_c_resolution_range_max_iterations_max_magnitude_mappings.gif
        '''
        # characters forbidden in file names
        forbidden_chars = re.compile(r'[~\\/:"*?<>|] ')

        # return file name with given parameters and forbidden characters replaced with '_'
        return os.path.join(self.target_directory, re.sub(forbidden_chars,'_', \
                            "julia_" + self.atractor + \
                            "_c=" + str(self.const) + \
                            (("_a=" + str(self.a)) if self.a else "") + \
                            (("_b=" + str(self.b)) if self.b else "") + \
                            (("_c=" + str(self.c)) if self.c else "") + \
                            "_res_" + str(self.res_w) + 'x' + str(self.res_h) + \
                            #"_ran_" + str(self.re_min) + '_' + str(self.re_max) + \
                            #    '_' + str(self.im_min) + '_' + str(self.im_max) + \
                            #"_iter_" + str(self.max_iter) + \
                            #"_mag_" + str(self.max_mag) + \
                            "_map_" + reduce(lambda x, y: x + "_" + y, self.maps) + \
                            ".gif"))

    # TODO:
    # - refactoring
    # renders Julia set as Image
    def render_frame(self, data:np.array) -> Image:
        '''Renders Julia set as numpy array'''
        z_arr = np.linspace(self.re_min, self.re_max, self.res_w) + 1j \
            * np.linspace(self.im_min, self.im_max, self.res_h)[:, np.newaxis]
        
        # calculate orbits
        self.if_in_julia_set_vectorized(z_arr, data)
        #self.if_in_mandelbrot_set(z_arr, data)

        # map data to colors
        data = self.render_color_mapping(data)

        # return image
        return Image.fromarray(data, 'RGB')

    # renders Julia set as Image with color shift
    # overloaded for sideways_slide_with_color_shift_and_const_shift function
    def render_frame_slide(self, data:np.array, color_shift:int=0) -> Image:
        '''Renders Julia set as numpy array with color shift'''
        z_arr = np.linspace(self.re_min, self.re_max, self.res_w) + 1j \
            * np.linspace(self.im_min, self.im_max, self.res_h)[:, np.newaxis]
        
        # calculate orbits
        self.if_in_julia_set_vectorized(z_arr, data)

        # shift colors
        data = (data + color_shift) % self.max_iter

        # map data to colors
        data = self.render_color_mapping(data)

        # return image
        return Image.fromarray(data, 'RGB')   

    def render_frame_uint16(self, color_map:str="twilight_shifted") -> Image:
        '''Renders Julia set as numpy array'''

    
        data = np.zeros((self.res_h, self.res_w), dtype=np.uint16)

        z_arr = np.linspace(self.re_min, self.re_max, self.res_w) + 1j \
            * np.linspace(self.im_max, self.im_min, self.res_h)[:, np.newaxis]
        
        
        # calculate orbits
        self.if_in_julia_set_vectorized(z_arr, data)

        # map data to colors
        # normalize orbits 
        normalized_orbits = data / self.max_iter
        # get colormap
        cmap = plt.colormaps[color_map]
        # map orbits
        pixels = (cmap(normalized_orbits)[:,:,:3] * 255).astype(np.uint8) # remove alpha channel

        # return image
        return Image.fromarray(pixels, 'RGB')

    # TODO
    # - refactoring
    # concatanates frames into .gif file
    def render(self, mode:str="1", range_:tuple=(-5,2), frames_amount=200, frame_duration:int=50):
        '''Concatanates frames into .gif file'''

        # initialize loading bar
        lb = LoadingBar(frames_amount)

        if mode == "1":
            # loop through frames
            frames = []
            for i, re in enumerate(np.linspace(range[0], range[1], frames_amount)):

                # update c_constant
                c = complex(re, 0)

                # render frame
                frames += [self.render_frame(c_constant=c)]

                # update loading bar
                lb.update(iteration=i+1, skip_every_other=50)

        elif mode == "2":

            c = 0.3336913831353 + 0.39768037241511j
            # loop through frames
            frames = []
            for i in range(frames_amount):

                # update range
                self.re_min += 0.0002
                self.re_max -= 0.0002
                self.im_min += 0.0002
                self.im_max -= 0.0002

                # render frame
                frames += [self.render_frame(c_constant=c, map="BuGn")]

                # update loading bar
                lb.update(iteration=i+1)

        elif mode == "3":
            c_constant = -0.8 + 0.156j

            # render image
            data = np.zeros((self.res_h, self.res_w), dtype=np.uint8)

            # loop through pixels
            for im in range(self.res_h):
                for re in range(self.res_w):

                    # calculate orbit and update data
                    z = self.pixel2complex(re, im)
                    data[im, re] = self.if_in_julia_set(c_constant, z)


            # loop through frames
            frames = []
            for i in range(frames_amount):

                frames += [Image.fromarray(self.map_plt_darker((data + i)%self.max_iter, 'BuGn'), 'RGB')]

                # update loading bar
                lb.update(iteration=i+1)

        # close loading bar
        lb.close()

        # save frames to .gif file
        frames[0].save(self.file_path(), format='GIF', append_images=frames[1:], save_all=True, duration=frame_duration, loop=0)

    def render_const_magnitude(self, frames_amount:int=200, frame_duration:int=50):

        # initialize loading bar
        lb = LoadingBar(frames_amount)

        # const value list
        const_values = self.const * np.exp(1j * np.linspace(0, 2 * np.pi, frames_amount))

        frames = []
        for i in range(frames_amount):
            data = np.zeros((self.res_h, self.res_w), dtype=np.uint8)
            self.const = const_values[i]

            frames.append(self.render_frame(data))

            lb.update(i+1)

        lb.close()

        frames[0].save(self.file_path(), format='GIF', append_images=frames[1:], \
                       save_all=True, duration=frame_duration, loop=0)

    def render_iter(self, frames_amount:int=100, frame_duration:int=50, log_spread=True):

        # initialize loading bar
        lb = LoadingBar(frames_amount)

        # list of max iterations
        # spread vaalues of max iter logarithmically to better see first elements
        # log_2_max_iter_start  - start of logarythmic scale (2^log_...)
        # log_2_max_iter_end    - end of logarythmic scale (2^log_...)
        # frames_amount         - how many elements to generate
        # False                 - not including log_2_max_iter_end as element (ensures not getting to limit of uint16 data type)
        # int                   - casts elements too ints
        log_2_max_iter_start = 4
        log_2_max_iter_end = 11
        if log_spread: iter_list = np.logspace(log_2_max_iter_start, log_2_max_iter_end, frames_amount, False, 2, int)
        else: iter_list = np.linspace(16, 2048, frames_amount, dtype=int)

        frames = []
        for i in range(frames_amount):
            
            self.max_iter = iter_list[i]

            frames.append(self.render_frame_uint16())

            lb.update(i+1)

        lb.close()

        frames[0].save(f"Julia_set_iter_{self.atractor}_res_{self.res_w}x{self.res_h}.gif", format='GIF', append_images=frames[1:], \
                        save_all=True, duration=frame_duration, loop=0)

    # TODO:
    # - problem with spacing ranges (seems jumpy, but maybe it's just the way it is displayed on my machine)
    #   definitely not check it on other machine and with mathemathition on university
    # Renders zoom effect from given start_range to given end_range into .gif file
    def render_zoom(self, start_range:tuple=(-2,2,-2,2), end_range:tuple=(-0.0002,0.0002,-0.0002,0.0002), \
                    frames_amount:int=200, frame_duration:int=50) -> None:
        '''Renders zoom effect from given start_range to given end_range into .gif file'''

        # initialize loading bar
        lb = LoadingBar(frames_amount)

        # helper variables        
        step = np.logspace(0, 1, frames_amount, base=10000)
        step_sum = sum(step)
        step = (step / step_sum)[::-1]
        zoom_factor_re_min = (end_range[0] - start_range[0])
        zoom_factor_re_max = (end_range[1] - start_range[1])
        zoom_factor_im_min = (end_range[2] - start_range[2])
        zoom_factor_im_max = (end_range[3] - start_range[3])
        self.re_min, self.re_max, self.im_min, self.im_max = start_range

        # loop through frames
        frames = []
        for i in range(frames_amount):

            # initialize data to zeros
            data = np.zeros((self.res_h, self.res_w), dtype=np.uint8)

            # update range
            self.re_min += zoom_factor_re_min * step[i]
            self.re_max += zoom_factor_re_max * step[i]
            self.im_min += zoom_factor_im_min * step[i]
            self.im_max += zoom_factor_im_max * step[i]

            # render frame
            frames.append(self.render_frame(data))

            # update loading bar
            lb.update(iteration=i+1)

        # close loading bar
        lb.close()

        # save frames to .gif file
        frames[0].save(self.file_path(), format='GIF', append_images=frames[1:], \
                       save_all=True, duration=frame_duration, loop=0)

    # TODO:
    # - refactoring (vectorize if possible)
    # Renders sideway slide with color shift and const value shift effect
    def sideway_slide_with_color_shift_and_const_shift(self, \
                                                       start_range:tuple=(-2,2,-2,2), \
                                                       const_list:list=[1+0j, 1+1j], \
                                                       slide_amount:int=4, \
                                                       frames_amount:int=400, frame_duration:int=50) -> None:
        '''
        Renders sideway slide with color shift and const value shift effect,
        from given start_range to 2Pi further,
        into .gif file
        Function goes through given list of points (const_list) 
        and renders Julia set for each constant complex value.
        Additionally it shifts color of each frame by 1/frames_amount * 256.
        Furthermore it shifts range of complex numbers by 8Pi/frames_amount.

        Parameters:
        - start_range: start range of complex numbers (tuple) (default: (-2,2,-2,2))
            (im_min, im_max, re_min, re_max)
        - const_list: list of complex numbers (points to go through) (list) (default: [1+0j, 1+1j])
        - frames_amount: amount of frames (int) (default: 400)
        - frame_duration: duration of each frame in ms (int) (default: 50)
        - slide_amount: shifts range by 2Pi * slide_amount (int) (default: 4)
        '''
        
        # how many segments
        segments = len(const_list)

        # ensure frames_amount is divisible by amount of segments
        fourth_frames = frames_amount // segments
        frames_amount = fourth_frames * segments

        # initialize loading bar
        lb = LoadingBar(frames_amount)
        
        # helper variables
        # 1D array of ranges starting from start_range and ending slide_amount * 2Pi further
        ranges = np.linspace(start_range, \
                            (start_range[0] + slide_amount*2*np.pi, start_range[1] + \
                             slide_amount*2*np.pi, start_range[2], start_range[3]), \
                            frames_amount)
        # 1D array of color shifts from 0 to 256
        color_shift = np.linspace(0, self.max_iter, frames_amount)
        # 1D array of smooth const shifts 
        # from const_list[0] to const_list[1] to const_list[2] to const_list[3] and so on.., than back to const_list[0]
        #spaced = tuple(np.vectorize(self.dense2less_dense2dense_distribiuion)(const_list[i], const_list[(i+1) % (segments-1)], fourth_frames + 1) for i in range(0, len(const_list)))
        spaced = tuple(np.linspace(const_list[i], const_list[(i+1) % (segments-1)], fourth_frames + 1) for i in range(0, len(const_list)))
        const_step = np.concatenate(spaced)
        

        # loop through frames
        frames = []
        for i, curr_range in enumerate(ranges):

            # update const and range
            self.const = const_step[i]
            self.re_min, self.re_max, self.im_min, self.im_max = curr_range

            # render frame
            frame = self.render_frame(np.zeros((self.res_h, self.res_w), dtype=np.uint8), color_shift[i])
            frames.append(frame)

            # update loading bar
            lb.update(iteration=i+1)

        # close loading bar
        lb.close()

        # save frames to .gif file
        frames[0].save(self.file_path(), format='GIF', append_images=frames[1:], \
                       save_all=True, duration=frame_duration, loop=0)

# RENDERING JULIA SETS AND RETURNING IT AS AN ARRAY
class julia2return_value(JuliaSetRenderer):
    pass
