"""
Julia set rendering classes.
Author: Wojciech Kośnik-Kowalczuk WKK
"""

# TODO:
# - dostosuj typy (uint8, uint8, npmath)
# - refaktoryzacja julia2gif
# - dodaj julia2return_value
# - dodaj mapowania:
#   wlasne (wartosc po wartosci)
# - mozesz dodac antyaliasing albo inna funkcjonalnosc poprawiajaca obraz
# - dodaj funkcje do renderowania obrazów o wielkiej rozdzielczosci
#   poprzez podzial na mniejsze obrazy i ich renderowanie osobno
#   zapisywanie do pliku skompresowanego np jpg i konkatanacje
# - file_path: dodaj mozliwosc wlasnej nazwy pliku
# - zmień format na jpg i mpg
# - julia2matplotlib
# - rozdziel klase na julia i mandelbrot

# TODO: (ideas for renders)
# - mandelbrot set
# - tabs in chrome
# - sin moving sideways
# - zoom
# - changing mag (and other parameters)
# - f(z) = z^alpha + c
# - f(z) = z^2 + c, c = 0.7885e^i*alpha, alpha = (0, 2pi)
# - mandelbrot to julia
# - burning ship

# IMPORTS
from __future__ import annotations
import sys
from .utils import parse_args
from .Julia_sets_renderers_classes import Julia2png, Julia2gif

# MAIN FUNCTION
def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    rnd = Julia2png(
        atractor="z^2+const",
        const=args.const,
        maps=[f"plt {args.cmap}"],
        resolution_w=args.resolution[0],
        resolution_h=args.resolution[1],
        range=args.plane,
    )

    rnd.render(vectorize_render=False)
    return 0

# ENTRY POINT
if __name__ == "__main__":
    raise SystemExit(main())