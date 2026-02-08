'''
Script for plotting complex functions in Pygame window.

Arguments:
sccrip_name (str),
plane range (num, num, num, num),
constant coefficient of atractor (num)

Created by Wojciech Kośnik-Kowalczuk
'''


# IMPORTS
import pygame
import sys
import math
import numpy as np


# MAIN CLASS
class PLOTTER():
    """
    Complex Plotter Class.

    Attributes:
    - NUM_OF_TICKS (int): Number of ticks on the axes.
    - OPTION_BAR_WIDTH (int): Width of the option bar.
    - OPTION_BAR_SPEED_OF_SLIDING (int): Speed of sliding for the option bar.
    - WINDOW_NAME (str): Name of the window.
    - WINDOW_SIZE (tuple): Default size of the window.

    Instance Attributes:
    - plane_range (tuple): Range of the complex plane to be plotted (re_min, re_max, im_min, im_max).
    - acttractor_str (str): String representation of the attractor.
    - fullscreen_height (int): Full screen height.
    - fullscreen_width (int): Full screen width.
    - windowscreen_height (int): Window screen height.
    - windowscreen_width (int): Window screen width.
    - screen_height (int): Screen height depending on the current screen mode.
    - screen_width (int): Screen width depending on the current screen mode.
    - is_fullscreen (bool): Flag indicating whether the window is in fullscreen mode.
    - flags (int): Pygame flags for window initialization.
    - screen (Surface): Pygame window surface.
    - option_bar_font_title (Font): Font for option bar title.
    - option_bar_font_text (Font): Font for option bar text.
    - option_bar_title (Surface): Surface for rendering the option bar title.
    - option_bar_description_txt (list): List containing option bar description strings.
    - option_bar_descriptiion (list): List containing surfaces for rendering option bar descriptions.
    - axes_font_numbers (Font): Font for rendering numbers on axes.
    - axes_font_names (Font): Font for rendering axis names.
    - optionBar_height (int): Size of the option bar.
    - optionBar_pos (int): Starting position of the side bar (off-window).
    - optionBar_toggle (bool): Flag indicating whether the option bar is toggled.
    - axes_color (tuple): Color of the axes.
    - show_axes (bool): Flag indicating whether the axes are visible.
    - axes_surface (Surface): Surface for rendering axes.

    Methods:

    Main loop:
    - draw_window(): Pygame window loop.

    Constructor:
    - __init__(): Constructor.
    - initialize_window(): Initialize Pygame module and prepare window.
    - initialize_text(): Initialize fonts and text.
    - initialize_optionBar_and_axes(): Initialize option bar and axes.
    - process_arguments(): Parses command line arguments.

    Helper functions:
    - draw_optionBar(): Draws option bar and updates it's position.
    - draw_axes_surface(): Draws axes and returns axes surface.
    - toggle_fullscreen(): Toggle fullscreen mode.
    - zoom_around_given_point(): Adjusts given range for zooming.
    """

    # Constants
    NUM_OF_TICKS = 8
    OPTION_BAR_WIDTH = 400
    OPTION_BAR_SPEED_OF_SLIDING = 8
    WINDOW_NAME = "Complex plotter"
    WINDOW_SIZE = (800, 1500)


    # MAIN LOOP
    # pygmame window loop
    def draw_window(self, image_generator: callable) -> None:

        # Main loop
        while True:

            # Interaction with user
            for event in pygame.event.get():
                
                # Exit window
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Keyboard
                if event.type == pygame.KEYDOWN:

                    # Toggle fullscreen by ressing F11 key
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

                    # Toggle option bar
                    if event.key == pygame.K_o: 
                        self.optionBar_toggle = not self.optionBar_toggle

                    # Closing with ESC key
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    # Changing axes color
                    if event.key == pygame.K_c:
                        self.axes_color = (0,0,0) if self.axes_color != (0,0,0) else (255,255,255)
                        self.axes_surface = self.draw_axes_surface()

                    # Show/hide axes
                    if event.key == pygame.K_a:
                        self.show_axes = not self.show_axes

                # Zoom range using mouse scroll
                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Zoom in
                    if event.button == 4: # scroll up
                        self.plane_range = self.zoom_around_given_point(pygame.mouse.get_pos(), 1.1)
                        self.axes_surface = self.draw_axes_surface()

                    # Zoom out
                    if event.button == 5: # scroll down
                        self.plane_range = self.zoom_around_given_point(pygame.mouse.get_pos(), 1/1.1)
                        self.axes_surface = self.draw_axes_surface()
                    

            self.screen.fill((0,0,0))
            # Draw something for demonstration (e.g., a red rectangle)
            #pygame.draw.rect(self.screen, (255, 0, 0), (100, 100, self.screen_width-200, self.screen_height-200))
            # Draw image
            img = image_generator(*self.plane_range, 100, 100)
            img = (img / np.max(img) * 255).astype(np.uint8)
            img_surface = pygame.image.frombuffer(img.tobytes(), (100, 100), 'P')
            self.screen.blit(img_surface, (0,0))

            # Axes
            if self.show_axes: self.screen.blit(self.axes_surface, (0,0))
            # Option bar
            self.draw_optionBar()

            # Update the display
            pygame.display.flip()


    # CONSTRUCTOR
    def __init__(self):
        # Arguments
        self.process_arguments()

        # Initialize rest of the variables
        self.initialize_window()
        self.initialize_text()
        self.initialize_optionBar_and_axes()
    
    # Initialize Pygame module and prepare window
    def initialize_window(self):
        '''Initialize Pygame module and prepare window'''

        # Initialize Pygame module and prepare window
        pygame.init()
        pygame.display.set_caption(self.WINDOW_NAME)

        # Full screen size
        self.fullscreen_height, self.fullscreen_width = pygame.display.Info().current_h, \
                                                        pygame.display.Info().current_w

        # Window screen size
        self.windowscreen_height, self.windowscreen_width = self.WINDOW_SIZE

        # Screen size depending on current screen mode
        self.screen_height, self.screen_width = self.fullscreen_height, self.fullscreen_width

        # Full screen mode flag
        self.is_fullscreen = True
        self.flags =  pygame.FULLSCREEN

        # Initialize window
        self.screen = pygame.display.set_mode((self.fullscreen_width, self.fullscreen_height), self.flags)
    
    # Initialize fonts and text
    def initialize_text(self): 
        '''Initialize fonts and text'''

        self.option_bar_font_title = pygame.font.Font(None, 65)
        self.option_bar_font_text = pygame.font.Font(None, 25)
        self.option_bar_title = self.option_bar_font_title.render('OPTION MENU', True, (0,0,0))
        self.option_bar_description_txt = ['To hide/show option menu press \'O\' key',
                                    'To enter/exit fullscreen mode press \'F11\' key',
                                    'To hide/show axes press \'A\' key',
                                    'To change colour of axes press \'C\' key',
                                    'To exit the program press \'ESC\' key',
                                    'Use mouse scroll to zoom in or out',
                                    '', '', '', '',
                                    'PARAMETERS:',
                                    'Atractor:   ' + self.acttractor_str,
                                    'Range: ']
        self.option_bar_descriptiion = [self.option_bar_font_text.render(t, True, (0,0,0)) for t in self.option_bar_description_txt]

        self.axes_font_numbers = pygame.font.Font(None, 25)
        self.axes_font_names = pygame.font.Font(None, 65)
    
    # Initialize option bar and axes
    def initialize_optionBar_and_axes(self):
        '''Initialize option bar and axes'''

        # Option bar
        self.optionBar_height = self.fullscreen_height # size of option bar
        self.optionBar_pos = self.fullscreen_width # starting position of side bar (off-window)
        self.optionBar_toggle = True

        # Axes
        self.axes_color = (255, 255, 255)
        self.show_axes = True
        self.axes_surface = self.draw_axes_surface()
    
    # Parses command line arguments
    def process_arguments(self) -> tuple:
        '''
        Processes arguments passed to the script.

        Returns:
        plane_range (tuple of 4 numbers): range of the complex plane to be plotted (re_min, re_max, im_min, im_max)
        acttractor_str (str): string representation of the atractor
        '''
        # constants
        AMOUNT_OF_ARGUMENTS = 6

        # Check if correct amount of arguments was passed
        if len(sys.argv) != AMOUNT_OF_ARGUMENTS: 
            raise ValueError("Script takes {} arguments (including scripts name), {} were given" 
                    .format(AMOUNT_OF_ARGUMENTS, len(sys.argv)))

        # Check if arguments are numbers
        try: self.plane_range = tuple(map(float, sys.argv[1:AMOUNT_OF_ARGUMENTS-1]))
        except: raise ValueError("Arguments 1 to 6 must be numbers")

        # get atracor
        self.acttractor_str = 'f(z) = z² + ' + sys.argv[5] # change to the regular expression later


    # HELPER FUNCTIONS
    # Draws option bar and updates it's position
    def draw_optionBar(self):
        '''Draws option bar and updates it's position'''

        # Slides option bar IN 
        if self.optionBar_toggle and self.optionBar_pos > self.screen_width - self.OPTION_BAR_WIDTH:
            self.optionBar_pos -= self.OPTION_BAR_SPEED_OF_SLIDING

        # Slides option bar OUT
        elif not self.optionBar_toggle and self.optionBar_pos < self.screen_width:
            self.optionBar_pos += self.OPTION_BAR_SPEED_OF_SLIDING

        # Add option bar surface to screen surface
        surf = pygame.Surface((self.OPTION_BAR_WIDTH, self.screen_height), pygame.SRCALPHA)
        surf.fill((200, 200, 200, 160))  # (R, G, B, alpha)
        self.screen.blit(surf, (self.optionBar_pos, 0))

        # Show options
        if self.optionBar_pos < self.screen_width - self.OPTION_BAR_WIDTH + self.OPTION_BAR_SPEED_OF_SLIDING:
            self.screen.blit(self.option_bar_title, (self.optionBar_pos + 45, 45))
            for index, t in enumerate(self.option_bar_descriptiion):
                self.screen.blit(t, (self.optionBar_pos + 16, 140 + index * 50))

    # Draws axes and returns axes surface
    def draw_axes_surface(self) -> object:
        '''Draws axes and returns axes surface'''

        # Create axes surface
        axes_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA) 

        # Unpack plane range
        re_min, re_max, im_min, im_max = self.plane_range

        # Real axis
        pygame.draw.line(
            axes_surface,
            self.axes_color,
            self.complex_to_screen(re_min, 0),
            self.complex_to_screen(re_max, 0),
            2
        )

        # Imaginary axis
        pygame.draw.line(
            axes_surface,
            self.axes_color,
            self.complex_to_screen(0, im_min),
            self.complex_to_screen(0, im_max),
            2
        )

        # Calculate tick intervals and precision based on plane_range
        x_tick_interval = (re_max - re_min) / (self.NUM_OF_TICKS - 1)
        y_tick_interval = (im_max - im_min) / (self.NUM_OF_TICKS - 1)
        order_of_magnitude_re = self.order_of_magnitude(x_tick_interval)
        order_of_magnitude_im = self.order_of_magnitude(y_tick_interval)

        # Calculate tick placement and draw them
        ticks_placement_re = ()
        ticks_placement_im = ()
        for t in range(self.NUM_OF_TICKS - 1):
            
            # Real
            # Draw ticks
            tick_re = re_min + t * x_tick_interval
            ticks_placement_re = self.complex_to_screen(tick_re, 0)
            # if statement excludes tick on the edge
            if t > 0:
                pygame.draw.line(
                    axes_surface,
                    self.axes_color,
                    (ticks_placement_re[0], ticks_placement_re[1] - 5),
                    (ticks_placement_re[0], ticks_placement_re[1] + 5),
                    2
                )
            # Draw numbers
            # if statement excludes 0 to avoid overlapping with other axis
            if ticks_placement_re[0]:
                axes_surface.blit(
                    self.axes_font_numbers.render(str(round(tick_re, 1 - order_of_magnitude_re)), True, self.axes_color),
                    (ticks_placement_re[0] - 5, ticks_placement_re[1] - 30)
                )

            # Imaginary
            # Draw ticks
            tick_im = im_min + t * y_tick_interval
            ticks_placement_im = self.complex_to_screen(0, tick_im)
            if t > 0:
                pygame.draw.line(
                    axes_surface,
                    self.axes_color,
                    (ticks_placement_im[0] - 5, ticks_placement_im[1]),
                    (ticks_placement_im[0] + 5, ticks_placement_im[1]),
                    2
                )
            # Draw numbers
            if ticks_placement_im[0]:
                axes_surface.blit(
                    self.axes_font_numbers.render(str(round(tick_im, 1 - order_of_magnitude_im)) + ' i', True,
                                                self.axes_color),
                    (ticks_placement_im[0] + 13, ticks_placement_im[1] - 7)
                )

        
        return axes_surface

    # Toggle fullscreen mode
    def toggle_fullscreen(self):
        '''Toggle fullscreen mode'''
        self.is_fullscreen = not self.is_fullscreen
        self.flags = pygame.FULLSCREEN if self.is_fullscreen else 0
        self.screen_height = self.fullscreen_height if self.is_fullscreen else self.windowscreen_height
        self.screen_width = self.fullscreen_width if self.is_fullscreen else self.windowscreen_width
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), self.flags)
        self.optionBar_pos = self.screen_width - self.OPTION_BAR_WIDTH if self.optionBar_toggle else self.screen_width
        self.axes_surface = self.draw_axes_surface()

    # Adjusts given range for zooming
    def zoom_around_given_point(self, point: tuple, zoom: float) -> tuple:
        '''
        Adjusts given range for zooming, zooms around given point.

        Arguments:
        point (tuple of 2 numbers): point around which the zoom will be performed (x, y)
        zoom (float): zoom factor

        Returns:
        range (tuple of 4 numbers): range of the complex plane to be plotted (re_min, re_max, im_min, im_max)
        '''
        # Calculate the complex number corresponding to the mouse position
        x, y = self.screen_to_complex(point[0], point[1])

        # Calculate the relative position of the mouse within the current axis range
        rel_re = (x - self.plane_range[0]) / (self.plane_range[1] - self.plane_range[0])
        rel_im = (y - self.plane_range[2]) / (self.plane_range[3] - self.plane_range[2])

        # Calculate the new range
        new_re_range = (self.plane_range[1] - self.plane_range[0]) / zoom
        new_im_range = (self.plane_range[3] - self.plane_range[2]) / zoom

        # Return the new minimum and maximum values of the range
        return x - rel_re * new_re_range, x + (1 - rel_re) * new_re_range, \
               y - rel_im * new_im_range, y + (1 - rel_im) * new_im_range

    # Returns the order of magnitude of x
    def order_of_magnitude(self, x: float) -> int:
        '''Returns the order of magnitude of x'''
        if x == 0: return 0 # log(0) is undifined
        return math.floor(math.log10(abs(x)))

    # Maps complex numbers to screen coordinates (pixels)
    def complex_to_screen(self, re_z:float, im_z:float) -> tuple[int, int]:
        '''
        Maps complex numbers to screen coordinates (pixels).

        Arguments:
        - re_z (float): Real part of the complex number.
        - im_z (float): Imaginary part of the complex number.

        Returns:
        tuple[int, int]: Screen coordinates (x, y).
        '''

        # Unpack plane range
        re_min, re_max, im_min, im_max = self.plane_range

        x = int(((re_z - re_min) / (re_max - re_min)) * self.screen_width)
        y = int(((im_max - im_z) / (im_max - im_min)) * self.screen_height)

        return x, y

    # Maps screen coordinates (pixels) to complex numbers
    def screen_to_complex(self, x: int, y: int) -> tuple[float, float]:
        '''
        Maps screen coordinates (pixels) to complex numbers.

        Arguments:
        - x (int): X-coordinate on the screen.
        - y (int): Y-coordinate on the screen.

        Returns:
        tuple[float, float]: Complex numbers (real, imaginary).
        '''

        # Unpack plane range
        re_min, re_max, im_min, im_max = self.plane_range

        re = (x / self.screen_width) * (re_max - re_min) + re_min
        im = im_max - (y / self.screen_height) * (im_max - im_min)

        return re, im

