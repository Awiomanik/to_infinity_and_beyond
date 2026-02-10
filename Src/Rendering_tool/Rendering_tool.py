#!/usr/bin/env python3
# Developt by: WKK

# TODO:
# - validate input for colors map selectionin handle_selection - cast_to_string

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import clear
import time
from Src.Rendering_tool.run_renderer import render
from Src.Utils.utils import DEFAULT_TXT, NEGATIVE_TXT, CLEAR_LINE_TXT
from .rendering_tool_constants import RENDERINF_TOOL_TITLE, RENDERING_TOOL_HELP_MESSAGE, OPTION_KEYS, FORMATS

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

# Create a key bindings object
kb = KeyBindings()
index = [0]  # Current index of selected option ([] for closere)

# Define actions for key bindings
@kb.add('up')
def _(event):
    index[0] = (index[0] - 1) % len(OPTION_KEYS)
    event.app.exit()

@kb.add('down')
def _(event):
    index[0] = (index[0] + 1) % len(OPTION_KEYS)
    event.app.exit()

@kb.add('enter')
def _(event):
    event.app.exit(OPTION_KEYS  [index[0]])

# Function to handle the selected option and perform corresponding actions
def handle_selection(selected: str, values: dict) -> bool:
    """
    Handle the action corresponding to the selected menu option.
    Args:
        selected: the key of the selected option
        values: dictionary of current parameter values
    Returns:
        bool: whether to continue the main loop (False to exit)
    """
    # Casting functions that convert user input string to the appropriate type for each option
    def cast_to_complex(input: str) -> complex | None:
        try:
            # Assuming complex input is given as 'real+imagj' or 'real-imagj'
            return complex(input)
        except ValueError:
            print("Invalid complex number. Please enter in the format real+imagj or real-imagj.")
            return None

    def cast_to_string(input: str) -> str:
        return input

    def cast_to_tuple(input: str) -> tuple[int, int] | None:
        try:
            temp = tuple(map(int, input.split(',')))
            if len(temp) != 2: return None
            return temp
        except ValueError:
            return None

    def cast_to_range_tuple(input: str):
        try:
            temp = tuple(map(float, input.split(',')))
        except:
            try:
                temp = tuple(map(int, input.split(',')))
            except ValueError:
                return None
        if len(temp) != 4: return None
        return temp

    # Map of option keys to their corresponding casting functions
    cast_functions = {
        'const': cast_to_complex,
        'map': cast_to_string,
        'resolution': cast_to_tuple,
        'range': cast_to_range_tuple,
    }
    
    # Main logic for handling the selected option
    if selected in cast_functions:

        # Loop until valid input is received or user cancels
        while True:
            input_str = prompt(\
f'Enter new value for {selected} (or type "cancel" to discard)\n\
{FORMATS[selected]}\n\
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
        print(RENDERINF_TOOL_TITLE)
        print(RENDERING_TOOL_HELP_MESSAGE)
        input("\n\nPress enter to go back to main menu")

    elif selected == 'render':
        print("initializing...\r", end='', flush=True)
        try:
            render(values)
        except Exception as e:
            print(f"\nRender failed: {e}")
        input("PRESS ENTER TO CONTINUE")
        return True
    
    else:
        print(f'{selected} option not recognized')

    return True

# Main 
def main():

    # main loop
    continue_flag = True
    while continue_flag:
        clear()
        print(RENDERINF_TOOL_TITLE)

        options_str = get_options_str(values)

        # print options with current selection highlighted
        for i, option in enumerate(options_str):
            if i == index[0]:
                # reverse colors to highlight current option
                print(f'{NEGATIVE_TXT}{option}{DEFAULT_TXT}')

            else:
                print(option)
            print()
        
        selected = prompt('\nUse arrow keys to navigate and Enter to choose option: ', \
                          key_bindings=kb, default=OPTION_KEYS[index[0]])
        
        if selected:
            print(CLEAR_LINE_TXT, end='')
            continue_flag = handle_selection(selected, values)


# ENTRY POINT
if __name__ == '__main__':
    main()
