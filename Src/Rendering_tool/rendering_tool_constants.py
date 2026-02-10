# -*- coding: utf-8 -*-
"""Constants used by the Rendering Tool."""

# TODO:
# - Finnish help message

# ASCII banner printed on CLI startup
RENDERINF_TOOL_TITLE ="""
____________  ___  _____ _____ ___  _      ______ _____ _   _______ ___________ ___________ 
|  ___| ___ \/ _ \/  __ \_   _/ _ \| |     | ___ \  ___| \ | |  _  \  ___| ___ \  ___| ___ \\
| |_  | |_/ / /_\ \ /  \/ | |/ /_\ \ |     | |_/ / |__ |  \| | | | | |__ | |_/ / |__ | |_/ /
|  _| |    /|  _  | |     | ||  _  | |     |    /|  __|| . ` | | | |  __||    /|  __||    / 
| |   | |\ \| | | | \__/\ | || | | | |____ | |\ \| |___| |\  | |/ /| |___| |\ \| |___| |\ \ 
\_|   \_| \_\_| |_/\____/ \_/\_| |_|_____/ \_| \_\____/\_| \_/___/ \____/\_| \_\____/\_| \_|
\n\n"""   

# Multiline help message shown in the HELP menu
RENDERING_TOOL_HELP_MESSAGE = """
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

# Option keys used for menu navigation: render, const, map, resolution, range, help, exit 
OPTION_KEYS = ['render', 'const', 'map', 'resolution', 'range', 'help', 'exit']

# Possible formats for user input when changing parameters in the menu (used in handle_selection)
FORMATS = {'const': "expected format is #+#j or #-#j (complex number)",
           'map': "possible color maps can be found at https://matplotlib.org/stable/gallery/color/colormap_reference",
           'resolution': "expected format #,# (width,height in pixels)",
           'range': "expected format: #,#,#,# (re_min, re_max, im_min, im_max where single values are floats)"}


