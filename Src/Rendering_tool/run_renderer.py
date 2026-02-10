#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renderer interface for the Rendering Tool.

Design assumptions:
- No rendering logic lives here.
- This module may raise exceptions if the renderer fails.
"""

from __future__ import annotations
import subprocess
import sys

rendering_module = "Src.Rendering_engine.Julia_sets_renderers"

def render(values: dict) -> None:
    """
    Invoke the Julia set renderer as a subprocess.

    Args:
        values (dict): Rendering parameters collected from the CLI.
            Expected keys:
                - 'const' (complex)
                - 'map' (str)
                - 'resolution' (tuple[int, int])
                - 'range' (tuple[float, float, float, float])

    Raises:
        FileNotFoundError: If the renderer script cannot be located.
        subprocess.CalledProcessError: If the renderer process fails.
    """

    cmap = values["map"]
    if isinstance(cmap, str) and cmap.startswith("plt "):
        cmap = cmap[4:]  # "plt twilight_shifted" -> "twilight_shifted"

    res_w, res_h = values["resolution"]
    resolution = f"{res_w}x{res_h}"  # (1000, 1000) -> "1000x1000"

    re_min, re_max, im_min, im_max = values["range"]
    plane = f"{re_min},{re_max},{im_min},{im_max}"  # (-2,2,-2,2) -> "-2,2,-2,2"

    command = [
        sys.executable,
        "-m",
        rendering_module,
        str(values["const"]),
        str(cmap),
        resolution,
        "--",
        plane,
    ]

    subprocess.run(command, check=True)
