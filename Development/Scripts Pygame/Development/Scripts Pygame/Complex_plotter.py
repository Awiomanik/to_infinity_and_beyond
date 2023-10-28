'''Arguments:
sccrip_name (str),
plane range (num, num, num, num),
constant coefficient of atractor (num)

Created by Wojciech Kośnik-Kowalczuk'''

import pygame
import sys
import math

# SCRIPT ARGUMENTS:
# Check if correct arguments were passed and assign them to proper varibles
amount_of_arguments = 6
if len(sys.argv) < amount_of_arguments: sys.exit("Script takes {} arguments, {} were given".format(amount_of_arguments, len(sys.argv)))
try: plane_range = tuple(map(float, sys.argv[1:amount_of_arguments]))
except: sys.exit("Arguments 1 to 6 must be numbers")
constant_coefficient = sys.argv[5]
'''plane_range = -2, 2, -2, 2
constant_coefficient = 2'''
acttractor_str = 'f(z) = z² + ' + str(constant_coefficient)

# Utility functions
# Maps complex numbers to screen coordinates
def complex_to_screen(re_z, im_z, width, height, plane_range):
    x = int(((re_z - plane_range[0]) / (plane_range[1] - plane_range[0])) * width)
    y = int(((plane_range[3] - im_z) / (plane_range[3] - plane_range[2])) * height)
    return x, y
def screen_to_complex(x, y, w, h, range):
    re = (x/w) * (range[1] - range[0]) + range[0]
    im = range[3] - (y/h) * (range[3] - range[2])
    return re, im

def order_of_magnitude(x):
    if x == 0: return 0 # log(0) is undifined
    return math.floor(math.log10(abs(x)))
# adjusts given range for zooming
def zoom_around_given_point(range, point, zoom):
    x, y = screen_to_complex(point[0], point[1], screen_width, screen_height, plane_range)
    # Calculate the relative position of the mouse within the current axis range
    rel_re = (x - range[0]) / (range[1] - range[0])
    rel_im = (y - range[2]) / (range[3] - range[2])
    # Calculate the new range
    new_re_range = (range[1] - range[0]) / zoom
    new_im_range = (range[3] - range[2]) / zoom
    # Return the new minimum and maximum values of the range
    return x-rel_re*new_re_range, x+(1-rel_re)*new_re_range, y-rel_im*new_im_range, y+(1-rel_im)*new_im_range

# Initialize Pygame module and prepare window
pygame.init()
pygame.display.set_caption('Complex plotter')
# initial window size = full screen resolution
fullscreen_height, fullscreen_width = pygame.display.Info().current_h, pygame.display.Info().current_w
# window screen size
windowscreen_height, windowscreen_width = 800, 1000
# screen size depending on current screen mode
screen_height, screen_width = fullscreen_height, fullscreen_width
is_fullscreen = True # variable for full screen mode flag
flags =  pygame.FULLSCREEN 
screen = pygame.display.set_mode((fullscreen_width, fullscreen_height), flags) # initialize window

# Fonts
option_bar_font_title = pygame.font.Font(None, 65)
option_bar_font_text = pygame.font.Font(None, 25)
option_bar_title = option_bar_font_title.render('OPTION MENU', True, (0,0,0))
option_bar_description_txt = ['To hide/show option menu press \'O\' key',
                              'To enter/exit fullscreen mode press \'F11\' key',
                              'To hide/show axes press \'A\' key',
                              'To change colour of axes press \'C\' key',
                              'To exit the program press \'ESC\' key',
                              'Use mouse scroll to zoom in or out',
                              '', '', '', '',
                              'PARAMETERS:',
                              'Atractor:   ' + acttractor_str,
                              'Range: ']
option_bar_descriptiion = [option_bar_font_text.render(t, True, (0,0,0)) for t in option_bar_description_txt]
option_bar_parameters = None # For future use
axes_font_numbers = pygame.font.Font(None, 25)
axes_font_names = pygame.font.Font(None, 65)

# Option bar
optionBar_width, optionBar_height = 400, fullscreen_height # size of option bar
optionBar_pos = fullscreen_width # starting position of side bar (off-window)
optionBar_speed_of_sliding = 8
optionBar_toggle = True
def optionBar_draw(toggle, pos, screen_w, screen_h, bar_w, speed, screen):
    # Slides option bar IN 
    if toggle and pos > screen_w - bar_w: pos -= speed
    # Slides option bar OUT
    elif not toggle and pos < screen_w: pos += speed
    # Add option bar surface to screen surface
    surf = pygame.Surface((bar_w, screen_h), pygame.SRCALPHA)
    surf.fill((200, 200, 200, 160)) # (R, G, B, alpha)
    screen.blit(surf, (pos, 0))
    # Show options
    if pos < screen_w - bar_w + speed:
        screen.blit(option_bar_title, (pos + 45, 45))
        for index, t in enumerate(option_bar_descriptiion): screen.blit(t, (pos + 16, 140 + index*50))
    # Return new position of option bar
    return pos

# Axes
axes_color = (255, 255, 255)
show_axes = True
def axes_surface_draw(color):
    axes_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA) 
    
    # Real axis
    pygame.draw.line(axes_surface, color,
                        complex_to_screen(plane_range[0], 0, screen_width, screen_height, plane_range),
                        complex_to_screen(plane_range[1], 0, screen_width, screen_height, plane_range), 2)
    # Imaginary axis
    pygame.draw.line(axes_surface, color,
                    complex_to_screen(0, plane_range[2], screen_width, screen_height, plane_range),
                    complex_to_screen(0, plane_range[3], screen_width, screen_height, plane_range), 2)
    
    # Calculate tick intervals and prcision based on plane_range
    num_of_ticks = 8
    x_tick_interval = (plane_range[1] - plane_range[0]) / (num_of_ticks-1)
    y_tick_interval = (plane_range[3] - plane_range[2]) / (num_of_ticks-1)
    order_of_magnitude_re = order_of_magnitude(x_tick_interval)
    order_of_magnitude_im = order_of_magnitude(y_tick_interval)

    # Calculate tick placement and draw them
    ticks_placement_re = ()
    ticks_placement_im = ()
    for t in range(num_of_ticks-1):
        # Real
        # Draw ticks
        tick_re = plane_range[0] + t * x_tick_interval
        ticks_placement_re = complex_to_screen(tick_re, 0, screen_width, screen_height, plane_range)
        # if statement excludes tick on the edge
        if t>0: pygame.draw.line(axes_surface, color, (ticks_placement_re[0], ticks_placement_re[1]-5), (ticks_placement_re[0], ticks_placement_re[1]+5), 2)
        # Draw numbers
        # if statement excludes 0 to avoid overlapping with othe axis
        if ticks_placement_re[0]: axes_surface.blit(axes_font_numbers.render(str(round(tick_re, 1-order_of_magnitude_re)), True, color), (ticks_placement_re[0]-5, ticks_placement_re[1]-30))
        
        # Imaginary
        # Draw ticks
        tick_im = plane_range[2] + t * y_tick_interval
        ticks_placement_im = complex_to_screen(0, tick_im, screen_width, screen_height, plane_range)
        if t>0: pygame.draw.line(axes_surface, color, (ticks_placement_im[0]-5, ticks_placement_im[1]), (ticks_placement_im[0]+5, ticks_placement_im[1]), 2)
        # Draw numbers
        if ticks_placement_im[0]: axes_surface.blit(axes_font_numbers.render(str(round(tick_im, 1-order_of_magnitude_im)) + ' i', True, color), (ticks_placement_im[0]+13, ticks_placement_im[1]-7))
    
    return axes_surface
axes_surface = axes_surface_draw(axes_color)


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
                is_fullscreen = not is_fullscreen
                flags = pygame.FULLSCREEN if is_fullscreen else 0
                screen_height = fullscreen_height if is_fullscreen else windowscreen_height
                screen_width = fullscreen_width if is_fullscreen else windowscreen_width
                screen = pygame.display.set_mode((screen_width, screen_height), flags)
                optionBar_pos = screen_width - optionBar_width if optionBar_toggle else screen_width
                axes_surface = axes_surface_draw(axes_color)
            # Toggle option bar
            if event.key == pygame.K_o: optionBar_toggle = not optionBar_toggle
            # Closing with ESC key
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            # Changing axes color
            if event.key == pygame.K_c:
                axes_color = (0,0,0) if axes_color != (0,0,0) else (255,255,255)
                axes_surface = axes_surface_draw(axes_color)
            # Show/hide axes
            if event.key == pygame.K_a: show_axes = not show_axes
        # Zoom range using mouse scroll
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: # scroll up
                plane_range = zoom_around_given_point(plane_range, pygame.mouse.get_pos(), 1.1)
                axes_surface = axes_surface_draw(axes_color)
            if event.button == 5: # scroll down
                plane_range = zoom_around_given_point(plane_range, pygame.mouse.get_pos(), 1/1.1)
                axes_surface = axes_surface_draw(axes_color)
            

    screen.fill((0,0,0))
    # Draw something for demonstration (e.g., a red rectangle)
    #pygame.draw.rect(screen, (255, 0, 0), (100, 100, screen_width-200, screen_height-200))

    # Axes
    if show_axes: screen.blit(axes_surface, (0,0))
    # Option bar
    optionBar_pos = optionBar_draw(optionBar_toggle, optionBar_pos, screen_width, screen_height, optionBar_width, optionBar_speed_of_sliding, screen)

    # Update the display
    pygame.display.flip()
