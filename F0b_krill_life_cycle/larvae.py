"""
Pictograms for the F0b diagram: the early life stages of Antarctic krill.

  egg()         egg
  nauplius()    nauplius, head up, as it swims towards the surface
  calyptopis()  calyptopis, facing right
  furcilia()    furcilia, facing right

Same conventions as the pictograms of the F0 diagram, whose helpers they are
built with: each function returns one pictogram as a shapely geometry, in its
own arbitrary units, with y pointing down. Details (eye, body segments) are
holes, so a pictogram is filled in a single colour.

The shapes are stylised, not anatomical drawings. They were drawn for this
presentation and are not taken from another source.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "F0_krill_predators_fishery"))
from pictograms import blob, circle, soften, stroke  # noqa: E402


def egg():
    return circle(0, 0, 10)


def nauplius():
    """Nauplius: oval body and three pairs of limbs."""
    body = blob(
        [(50, 6), (70, 20), (78, 48), (68, 80), (50, 96), (32, 80), (22, 48), (30, 20)]
    )
    limbs = []
    for sign in (-1, 1):
        for pts in (
            [(18, 26), (32, 8), (38, -10)],
            [(24, 46), (44, 36), (56, 18)],
            [(20, 64), (38, 66), (50, 56)],
        ):
            limbs.append(stroke([(50 + sign * dx, y) for dx, y in pts], 6))
    return soften(unary_union([body, *limbs]), 1.0)


def calyptopis():
    """Calyptopis: rounded carapace over the eyes, slender forked abdomen."""
    carapace = blob(
        [
            (206, 52),
            (194, 28),
            (164, 16),
            (130, 20),
            (108, 38),
            (102, 58),
            (116, 76),
            (150, 84),
            (184, 78),
            (202, 66),
        ]
    )
    abdomen = stroke([(112, 56), (72, 59), (34, 62)], 17, cap="flat")
    fork = [
        stroke([(38, 62), (16, 52), (2, 42)], 7),
        stroke([(38, 62), (16, 72), (2, 82)], 7),
    ]
    limbs = [
        stroke([(170, 78), (176, 96), (188, 108)], 6),
        stroke([(150, 82), (153, 102), (162, 116)], 6),
        stroke([(130, 80), (130, 98), (136, 112)], 6),
    ]
    antennae = [
        stroke([(202, 50), (220, 40), (236, 26)], 6),
        stroke([(204, 60), (224, 60), (242, 52)], 6),
    ]
    g = soften(unary_union([carapace, abdomen, *fork, *limbs, *antennae]), 1.0)
    gaps = [stroke([(x, 44), (x, 74)], 4, smooth=False) for x in (94, 76, 58)]
    eye = circle(180, 50, 9) - circle(180, 50, 4)
    return g - unary_union([*gaps, eye])


def furcilia(pleopods=5):
    """Furcilia: a small krill with large stalked eyes. The swimming legs
    appear through the furcilia stages; `pleopods` is the number of pairs
    drawn (0 to 5)."""
    body = blob(
        [
            (322, 80, "c"),
            (300, 66),
            (268, 58),
            (236, 58),
            (204, 62),
            (170, 68),
            (136, 76),
            (104, 90),
            (78, 108),
            (58, 126),
            (34, 138),
            (10, 142, "c"),
            (30, 150),
            (52, 148),
            (72, 138),
            (92, 124),
            (116, 110),
            (144, 102),
            (174, 100),
            (204, 102),
            (240, 106),
            (276, 106),
            (304, 100),
            (318, 90),
        ]
    )
    eye = circle(334, 94, 15)
    ant = [
        stroke([(318, 80), (344, 64), (366, 44)], 5),
        stroke([(322, 84), (350, 78), (374, 68)], 5),
    ]
    legs = []
    for i, x in enumerate(np.linspace(300, 248, 3)):
        ln = 26 + 3 * i
        legs.append(
            stroke([(x, 102), (x + 4, 102 + 0.55 * ln), (x + 14, 102 + ln)], 5)
        )
    top = [(204, 62), (170, 68), (136, 76), (104, 90), (78, 108)]
    bot = [(204, 102), (174, 100), (144, 102), (116, 110), (92, 124)]
    pleo, gaps = [], []
    for i, ((xt, yt), (xb, yb)) in enumerate(zip(top, bot)):
        gaps.append(stroke([(xt + 2, yt - 4), (xb + 2, yb + 4)], 4, smooth=False))
        if i >= pleopods:
            continue
        mx, my = xb - 14, yb + (1.5 if i < 2 else 4 + 2.2 * (i - 1))
        pleo.append(
            blob(
                [
                    (mx + 6, my - 2, "c"),
                    (mx + 3, my + 12),
                    (mx - 10, my + 24, "c"),
                    (mx - 7, my + 8),
                    (mx - 6, my - 2, "c"),
                ]
            )
        )
    tail_gap = stroke([(60, 120), (72, 142)], 4, smooth=False)
    g = soften(unary_union([body, *ant, *legs, *pleo]), 0.8)
    g = g - unary_union([*gaps, tail_gap])
    ring = eye.buffer(4) - eye
    return (g - ring).union(eye) - circle(338, 90, 4)
