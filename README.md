# To infinity and beyond
> **still in development**

This repository contains a collection of fractal algorithms and visualization tools aimed at exploring the fascinating world of fractals, developed as a learning endeavour to deepen my understanding of both programming and complex mathematical concepts.

Explore various fractals with Python scripts and Jupyter notebooks. This project is aimed at learning coding and exploring math.

## Table of Contents
- [Objectives](#objectives)
- [Content](#content)
- [Usage](#Usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Disclaimer](#disclaimer)

## Objectives

- Gain a deep understanding of the mathematical theories underlying fractals.
- Translate mathematical models into efficient programmatic algorithms.
- Enhance skills in Python programming and computational mathematics.

## Content:

└── **Tools** <br>
&nbsp;&nbsp;&nbsp;&nbsp;└── [Complex_plotter.py](Complex_plotter.py)<br>
<!-- indent the block below somehow later -->
This script serves as a complex plotter using Pygame, aimed at aiding in the visualization of fractals. This is a proof-of-concept and will probably not be used directly in the final project. It serves as a sandbox for exploring and implementing a variety of functionalities and concepts such as full-screen display, command-line argument processing, and complex number visualization.

## Usage:

- **[Complex_plotter.py](Complex_plotter.py)**<br>
In the directory of plotter run console command:<br>
`python script_name.py [plane_range1] [plane_range2] [plane_range3] [plane_range4] [constant_coefficient]`<br>
**Parameters:**<br>
`plane_range`: A tuple indicating the range of the complex plane to be plotted ($R_{min}, R_{max}, I_{min}, I_{max}$).<br>
`constant_coefficient`: The coefficient for the fractal attractor.
$$a(z) = z^{2} + constant\ coefficiant$$

## Features
- Interactive Python notebooks for learning about various fractal sets, including the Mandelbrot set, Julia sets, and more.
- An interactive user interface for dynamically exploring different fractal patterns.
- Options for customizing parameters to generate unique fractal shapes.
- Lots of fractals ;)
  
## Contributing
Contributions are more than welcome!<br>
Feel free to submit pull requests or report issues. This project serves not only as an educational resource but also as a platform for collective problem-solving and programming practice.

## License
This project is licensed under the Apache License v2.0 - see the [LICENSE](LICENSE) file for details.

## Credits
Developt by Wojciech Kośnik-Kowalczuk.<br>
All fractals where generated by software contained in this repository.<br>
<!--
This project was informed and inspired by a variety of sources, including academic lectures, online resources, and published literature. I extend my gratitude to the following:
- dr... & mgr... for foundational concepts and direct guidance provided during *Wstęp do programowania* cours at the [Faculty of Mathematics](https://wmat.pwr.edu.pl/) of [Wrocław University of Science and Technology](https://pwr.edu.pl/en/).
- [Title of Book or Article](link to the source) by [Author(s)].
- Any other individuals, communities, or organizations that contributed to your learning or supported the project in any way.-->

## Disclaimer
This project is primarily an educational endeavour and may not be optimized for all systems. Use at your own risk.

