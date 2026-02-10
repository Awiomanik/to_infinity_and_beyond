from __future__ import annotations
import argparse
from dataclasses import dataclass
from typing import Tuple
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class RenderArgs:
    const: complex
    cmap: str
    resolution: Tuple[int, int]
    plane: Tuple[float, float, float, float]


def _complex_type(s: str) -> complex:
    try:
        return complex(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid complex number: {s}") from e


def _resolution_type(s: str) -> Tuple[int, int]:
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception as e:
        raise argparse.ArgumentTypeError("Resolution must be like 1000x1000") from e


def _plane_type(s: str) -> Tuple[float, float, float, float]:
    try:
        vals = [float(v) for v in s.split(",")]
        if len(vals) != 4:
            raise ValueError
        return tuple(vals)  # type: ignore
    except Exception as e:
        raise argparse.ArgumentTypeError(
            "Plane must be re_min,re_max,im_min,im_max"
        ) from e


def _cmap_type(s: str) -> str:
    if s not in plt.colormaps:
        raise argparse.ArgumentTypeError(f"Unknown colormap: {s}")
    return s


def parse_args(argv: list[str]) -> RenderArgs:
    parser = argparse.ArgumentParser(prog="render_julia")

    parser.add_argument("const", type=_complex_type)
    parser.add_argument("cmap", type=_cmap_type)
    parser.add_argument("resolution", type=_resolution_type)
    parser.add_argument("plane", type=_plane_type)

    ns = parser.parse_args(argv)

    return RenderArgs(
        const=ns.const,
        cmap=ns.cmap,
        resolution=ns.resolution,
        plane=ns.plane,
    )
