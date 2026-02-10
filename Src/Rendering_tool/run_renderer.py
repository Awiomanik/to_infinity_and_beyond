#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renderer interface for the Rendering Tool.

Design assumptions:
- No rendering logic lives here.
- Paths are resolved relative to the repository structure, not CWD.
- This module may raise exceptions if the renderer fails.
"""

from __future__ import annotations
import subprocess
import sys
from pathlib import Path

# renderer lives in: Src/Rendering_engine/Julia_sets_renderers.py
repo_root = Path(__file__).resolve().parents[2]   # .../Src/Rendering_tool/run_render.py -> repo root
rendering_script_path = repo_root / "Src" / "Rendering_engine" / "Julia_sets_renderers.py"

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

    if not rendering_script_path.exists():
        raise FileNotFoundError(f"Renderer script not found: {rendering_script_path}")

    command = [
        sys.executable,
        str(rendering_script_path),
        str(values["const"]),
        str(values["map"]),
        str(values["resolution"]),
        str(values["range"]),
    ]

    subprocess.run(command, check=True)
