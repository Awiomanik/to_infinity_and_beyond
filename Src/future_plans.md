this file contains list of features, improvments and generally ideas of what can be added to the project and what I want it to look like in the future.

# TODO:

### General:
- [x] clean up file structure
- [ ] Add main script for users in the main catalog
- [ ] Render graphics and table for main document
- [ ] Prepare implementation chapter for main document
- [ ] configure README.md file
- [ ] add Sierpiński and maybe other like perlin noise
- [ ] add readme.md to google drive
  

### Julia_set_renderers:
- [ ] Adjust types in arrays (uint8, uint16,..) and calculations (npmath for better precision)
- [ ] Refactor julia2gif
- [ ] Add julia2return_value
- [ ] Add mappings:
    - Custom (value to value)
- [ ] Integrate anti-aliasing when ready
- [ ] Introduce functions for rendering high-resolution images by dividing them into smaller images and rendering them separately, then saving to a compressed file such as jpg, and finally concatenating them
- [ ] file_path: Add the option to specify a custom file name
- [ ] finnish help message in rendering_tool_constants
- [ ] validate input for colors map selectionin in rendering_tool


### If time allows:
- [ ] Add interactive tool for users (using plotters files)
- [ ] Build antialiasing tool


### Ideas for renderers:
- [x] trigonometric functions
- [ ] mandelbrot set (seems correct but needs to be tested)
- [ ] examples saved as tabs in chrome 
- [ ] sin moving sideways
- [ ] zoom (problem with range adjustment)
- [ ] changing mag (and other parameters)
- [ ] f(z) = z^alpha + c
- [ ] f(z) = z^2 + c, c = 0.7885e^i*alpha, alpha = (0, 2pi)
- [ ] mandelbrot to julia and vice versa
- [ ] burning ship