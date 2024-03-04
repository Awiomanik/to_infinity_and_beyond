#!/usr/bin/env python3
# Developt by: WKK

# TODO:
# - finnish help string

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import clear
import subprocess
import os
import time

title ="""
____________  ___  _____ _____ ___  _      ______ _____ _   _______ ___________ ___________ 
|  ___| ___ \/ _ \/  __ \_   _/ _ \| |     | ___ \  ___| \ | |  _  \  ___| ___ \  ___| ___ \\
| |_  | |_/ / /_\ \ /  \/ | |/ /_\ \ |     | |_/ / |__ |  \| | | | | |__ | |_/ / |__ | |_/ /
|  _| |    /|  _  | |     | ||  _  | |     |    /|  __|| . ` | | | |  __||    /|  __||    / 
| |   | |\ \| | | | \__/\ | || | | | |____ | |\ \| |___| |\  | |/ /| |___| |\ \| |___| |\ \ 
\_|   \_| \_\_| |_/\____/ \_/\_| |_|_____/ \_| \_\____/\_| \_/___/ \____/\_| \_\____/\_| \_|
\n\n"""   

help_message = """
Welcome to the Fractal Renderer!

This nifty tool is your gateway to the mesmerizing world of Julia set fractals. Dive in and bring mathematical beauty to life!


Navigating the Main Menu

To explore your options:
- Use \u2191 and \u2193 (arrow keys) to glide through the actions available.
- Press the Enter key to select the \033[7mhighlighted\033[0m option.


What's on the Menu?

- RENDER: Select this, and we'll start painting the fractal PNG picture with the parameters you've set, visible right on your screen.

... (to be continued)


For more information about fractal rendering, we highly encourage You to familiarize with main document included in this paper:
"Holomorphic_dynamics_an_Odyssey_from_Chaos_to_Art"
"""

# Define default values
values = {
    'const': 0.285 + 0.01j,
    'map': "twilight_shifted",
    'resolution': (600, 600),
    'range': (-1.5, 1.5, -1.5, 1.5)
}

# Define the menu options based on values
def get_options_str(values):
    return [
        'RENDER',
        f'const = {values["const"]}',
        f'map = {values["map"]}',
        f'resolution = {values["resolution"][0]}x{values["resolution"][1]}',
        f'range = {values["range"]}',
        'help',
        'EXIT'
    ]

# Define options keys
options_keys = ['render', 'const', 'map', 'resolution', 'range', 'help', 'exit']

# Create a key bindings object
kb = KeyBindings()
index = [0]  # Current index of selected option ([] for closere)

# Define actions for key bindings
@kb.add('up')
def _(event):
    index[0] = (index[0] - 1) % len(options_keys)
    event.app.exit()

@kb.add('down')
def _(event):
    index[0] = (index[0] + 1) % len(options_keys)
    event.app.exit()

@kb.add('enter')
def _(event):
    event.app.exit(options_keys[index[0]])

def cast_to_complex(input_str):
    try:
        # Assuming complex input is given as 'real+imagj' or 'real-imagj'
        return complex(input_str)
    except ValueError:
        print("Invalid complex number. Please enter in the format real+imagj or real-imagj.")
        return None

def cast_to_string(input_str):
    # TODO:
    # - validate input
    return input_str

def cast_to_tuple(input_str):
    try:
        temp = tuple(map(int, input_str.split(',')))
        if len(temp) != 2: return None
        return temp
    except ValueError:
        return 

def cast_to_range_tuple(input_str):
    try:
        temp = tuple(map(float, input_str.split(',')))
    except:
        try:
            temp = tuple(map(int, input_str.split(',')))
        except ValueError:
            return None
    if len(temp) != 4: return None
    return temp

cast_functions = {
    'const': cast_to_complex,
    'map': cast_to_string,
    'resolution': cast_to_tuple,
    'range': cast_to_range_tuple,
}

formats = {'const': "expected format is #+#j or #-#j (complex number)",
           'map': "possible color maps can be found at https://matplotlib.org/stable/gallery/color/colormap_reference",
           'resolution': "expected format #,# (width,height in pixels)",
           'range': "expected format: #,#,#,# (re_min, re_max, im_min, im_max where single values are floats)"}

def handle_selection(selected, values):
    if selected in cast_functions:
        while True:
            input_str = prompt(\
f'Enter new value for {selected} (or type "cancel" to discard)\n\
{formats[selected]}\n\
==> [Enter value]: ')

            if input_str.lower() == 'cancel':
                print(f'\nCancelled updating {selected}.')
                time.sleep(0.7)
                break

            new_value = cast_functions[selected](input_str)

            if new_value is not None:
                values[selected] = new_value
                print(f'\nUpdated {selected} to {new_value}')
                time.sleep(0.7)
                break
            
            else:
                # clear output
                print("\033[1A\033[2K" * 5, end='')
                print("Wrong format, please try again.\n")

    elif selected == 'exit':
        clear()
        return False
    
    elif selected == 'help':
        clear()
        print(title)
        print(help_message)
        input("\n\nPress enter to go back to main menu")

    
    elif selected == 'render':
        print("initializing...\r", end='', flush=True)
        render(values)
        print("\nPicture rendered, you can find it in current catalog")
        input("PRESS ENTER TO CONTINUE")
        return True
    
    else:
        print(f'{selected} option not recognized')
    return True

def render(values):
    script_path = os.path.join(os.getcwd(), "Utils", "Renderers_still_in_development", "Julia_sets_renderers.py")
    command = ["python", script_path, str(values['const']), str(values['map']), str(values['resolution']), str(values['range'])]

    try:
        subprocess.call(command)
    except subprocess.CalledProcessError as e:
        print("Error running the script:", e)

def main():
    continue_flag = True
    while continue_flag:
        clear()
        print(title)

        options_str = get_options_str(values)

        for i, option in enumerate(options_str):
            if i == index[0]:
                # reverse colors to highlight current option
                print(f'\033[7m{option}\033[0m')

            else:
                print(option)
            print()
        
        selected = prompt('\nUse arrow keys to navigate and Enter to choose option: ', \
                          key_bindings=kb, default=options_keys[index[0]])
        
        if selected:
            print("\033[1A\033[2K", end='')
            continue_flag = handle_selection(selected, values)


# EXECUTE
if __name__ == '__main__':
    main()
