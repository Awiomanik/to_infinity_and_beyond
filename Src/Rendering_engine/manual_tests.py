from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .Julia_sets_renderers_classes import Julia2png, Julia2gif


@dataclass(frozen=True)
class Scenario:
    name: str
    run: Callable[[], None]
    notes: str = ""


def scenarios() -> list[Scenario]:
    items: list[Scenario] = []

    # 1) Basic PNG render
    def png_basic() -> None:
        rnd = Julia2png(
            atractor="z^2+const",
            const=-0.8 + 0.156j,
            maps=["plt twilight_shifted"],
            resolution_w=1000,
            resolution_h=1000,
            range=(-2, 2, -2, 2),
        )
        rnd.render(vectorize_render=False)

    items.append(Scenario(
        name="png_basic_twilight",
        run=png_basic,
        notes="Basic sanity check: PNG, single colormap."
    ))

    # 2) GIF: const magnitude rotation
    def gif_const_magnitude() -> None:
        rnd = Julia2gif(
            atractor="z^2 + const",
            const=-0.29609091 + 0.62491j,
            maps=["plt twilight_shifted"],
            resolution_w=800,
            resolution_h=800,
            range=(-0.9, 0.3, -0.3, 0.9),
            max_ieration=256,
            max_magnitude=2,
        )
        rnd.render_const_magnitude(frames_amount=200, frame_duration=50)

    items.append(Scenario(
        name="gif_const_magnitude",
        run=gif_const_magnitude,
        notes="Const rotates on circle (magnitude fixed)."
    ))

    return items


def run(name: str) -> None:
    for sc in scenarios():
        if sc.name == name:
            sc.run()
            return
    raise SystemExit(f"Unknown scenario: {name}\nAvailable: {[s.name for s in scenarios()]}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: python -m Src.Rendering_engine.manual_tests <scenario_name>")
    run(sys.argv[1])