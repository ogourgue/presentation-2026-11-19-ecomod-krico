"""
F0 plot: Antarctic krill between its predators and the fishery.

A diagram, not a data figure. Krill is in the middle. Its predators are on
the left, drawn as one group (humpback whale, crabeater seal, Adelie penguin,
Antarctic prion, mackerel icefish), and a krill trawler is on the right. One
arrow runs from each side to the krill; the predators are gathered around
theirs.

The width of the shaft of each arrow is proportional to the amount of krill
taken per year: what the predators eat on the left, what the fishery catches
on the right. The predators' amount is a range, and their arrow is drawn for
the middle of it. The arrowheads are not to scale. Each arrow carries its
amount.

The pictograms come from pictograms.py. This script scales them, places them,
and draws the arrows and their labels, on a transparent background. The
pictograms are in one colour and the arrows and their amounts in another. The
details of the pictograms are holes.

Inputs:  none
Output:  krill_predators_fishery.png
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath
from shapely import affinity
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

import pictograms


# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------
#
# Krill taken per year, in million tonnes (Mt).
#
# Predators: consumption by the main krill predators (fish, penguins, flying
# seabirds, seals and whales) in the Scotia Sea and Antarctic Peninsula
# region, as a range (Saunders et al., 2019, Table 7). The arrow is drawn for
# the middle of the range.
#
# Fishery: the catch limit in force in Subareas 48.1 to 48.4, also called the
# trigger level, reached for the first time in 2025 (Meyer et al., 2025).

CONSUMPTION_MIN = 34.3
CONSUMPTION_MAX = 61.3
CONSUMPTION = (CONSUMPTION_MIN + CONSUMPTION_MAX) / 2
CATCH = 0.62

CONSUMPTION_LABEL = "34–61 Mt\nper year"
CATCH_LABEL = "0.62 Mt\nper year"


# ---------------------------------------------------------------------------
# Style and layout
# ---------------------------------------------------------------------------
#
# Lengths are in hundredths of an inch, with the origin at the top left and
# y pointing down.

mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 14,
    "figure.figsize": (9.32, 3.74),
})

COLOR = "#222222"
ARROW_COLOR = "#5E84D2"

# Distance between the outer pictograms and the left and right edges.
MARGIN = 8

# Krill, in the centre.
KRILL_WIDTH = 184

# Predators: pictogram, width or height, left edge and top edge. They form a
# group around their arrow: the whale and the prion above it, the seal behind
# it, the icefish and the penguin below it.
PREDATORS = (
    (pictograms.whale, {"w": 240}, 8, 16),
    (pictograms.seal, {"w": 190}, 8, 157),
    (pictograms.icefish, {"w": 212}, 12, 296),
    (pictograms.penguin, {"h": 106}, 240, 256),
    (pictograms.prion, {"w": 112}, 262, 30),
)

# Trawler: width, and the fraction of its height (from the top) that is level
# with the krill, so that the arrow leaves from the hull.
TRAWLER_WIDTH = 250
TRAWLER_LEVEL = 0.70

# Arrows. The shaft is ARROW_SCALE wide per Mt per year. The head of the
# predator arrow is sized from its shaft; the head of the fishery arrow has a
# fixed size, large enough to be seen.
ARROW_SCALE = 1.7
ARROW_GAP = 13
HEAD_WIDTH_RATIO = 1.5
HEAD_LENGTH_RATIO = 0.55
MIN_HEAD_WIDTH = 9
MIN_HEAD_LENGTH = 11

# Distance between the fishery arrow and the bottom of its label.
LABEL_GAP = 7


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def fit(geom, w=None, h=None):
    """Scale geom to width w or height h (to the smaller scale if both)."""
    x0, y0, x1, y1 = geom.bounds
    s = min(
        w / (x1 - x0) if w else math.inf,
        h / (y1 - y0) if h else math.inf,
    )
    return affinity.scale(geom, s, s, origin=(x0, y0))


def put(geom, cy=None, top=None, left=None, right=None, cx=None):
    """Move geom. Vertically: centre at cy, or top edge at `top`.
    Horizontally: left edge at `left`, right edge at `right`, or centre at
    `cx`."""
    x0, y0, x1, y1 = geom.bounds
    if left is not None:
        dx = left - x0
    elif right is not None:
        dx = right - x1
    else:
        dx = cx - (x0 + x1) / 2
    dy = top - y0 if top is not None else cy - (y0 + y1) / 2
    return affinity.translate(geom, dx, dy)


def arrow(x_start, x_end, y, width):
    """Horizontal arrow at height y, with a shaft of the given width.
    Returns the polygon and the x-range of the shaft."""
    head_width = max(HEAD_WIDTH_RATIO * width, MIN_HEAD_WIDTH)
    head_length = max(HEAD_LENGTH_RATIO * width, MIN_HEAD_LENGTH)
    d = 1 if x_end > x_start else -1
    x_base = x_end - d * head_length
    shaft = Polygon([
        (x_start, y - width / 2),
        (x_base + d, y - width / 2),
        (x_base + d, y + width / 2),
        (x_start, y + width / 2),
    ])
    head = Polygon([
        (x_end, y),
        (x_base, y - head_width / 2),
        (x_base, y + head_width / 2),
    ])
    return unary_union([shaft, head]), sorted((x_start, x_base))


def compose(width, height):
    """The pictograms, the two arrows and the anchor points of their labels,
    on a canvas of width x height."""
    cx, cy = width / 2, height / 2

    krill = put(fit(pictograms.krill(), w=KRILL_WIDTH), cy=cy, cx=cx)

    predators = [
        put(fit(pictogram(), **size), top=top, left=left)
        for pictogram, size, left, top in PREDATORS
    ]
    seal = predators[1]

    trawler = fit(pictograms.trawler(), w=TRAWLER_WIDTH)
    x0, y0, x1, y1 = trawler.bounds
    trawler = affinity.translate(
        trawler,
        width - MARGIN - x1,
        cy - (y0 + TRAWLER_LEVEL * (y1 - y0)),
    )

    eaten, (xa, xb) = arrow(
        seal.bounds[2] + ARROW_GAP,
        krill.bounds[0] - ARROW_GAP,
        cy,
        ARROW_SCALE * CONSUMPTION,
    )
    caught, (xc, xd) = arrow(
        trawler.bounds[0] - ARROW_GAP,
        krill.bounds[2] + ARROW_GAP,
        cy,
        ARROW_SCALE * CATCH,
    )

    pictos = [krill, *predators, trawler]
    arrows = [eaten, caught]
    for shape in pictos + arrows:
        x0, y0, x1, y1 = shape.bounds
        if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
            raise ValueError(f"shape outside the canvas: {shape.bounds}")

    # The predator label sits in the shaft and may reach into the head; the
    # fishery label sits above the arrow.
    head_reach = 0.25 * HEAD_LENGTH_RATIO * ARROW_SCALE * CONSUMPTION
    labels = {
        "eaten": ((xa + xb + head_reach) / 2, cy),
        "caught": ((xc + xd + MIN_HEAD_LENGTH) / 2, cy - LABEL_GAP),
    }
    return pictos, arrows, labels


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def to_patch(geom, color):
    """Filled patch of a polygon or multipolygon, holes included."""
    polygons = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    vertices, codes = [], []
    for polygon in polygons:
        # Exterior and holes wound in opposite directions, so that the holes
        # are left empty.
        polygon = orient(polygon, 1.0)
        for ring in [polygon.exterior, *polygon.interiors]:
            xy = np.asarray(ring.coords)
            vertices.append(xy)
            codes.append(
                [MplPath.MOVETO]
                + [MplPath.LINETO] * (len(xy) - 2)
                + [MplPath.CLOSEPOLY]
            )
    return PathPatch(
        MplPath(np.vstack(vertices), np.concatenate(codes)),
        facecolor=color,
        edgecolor="none",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "krill_predators_fishery.png",
    )
    args = parser.parse_args()

    fig = plt.figure()
    width, height = (100 * v for v in fig.get_size_inches())
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    pictos, arrows, labels = compose(width, height)
    for shape in pictos:
        ax.add_patch(to_patch(shape, COLOR))
    for shape in arrows:
        ax.add_patch(to_patch(shape, ARROW_COLOR))
    ax.text(
        *labels["eaten"], CONSUMPTION_LABEL,
        color="white", ha="center", va="center", linespacing=1.15,
    )
    ax.text(
        *labels["caught"], CATCH_LABEL,
        color=ARROW_COLOR, ha="center", va="bottom", linespacing=1.15,
    )

    fig.savefig(args.output, dpi=500, transparent=True)
    print(
        f"wrote {args.output}  "
        f"(predators : fishery = {CONSUMPTION / CATCH:.0f} : 1, "
        f"from {CONSUMPTION_MIN / CATCH:.0f} to {CONSUMPTION_MAX / CATCH:.0f})"
    )


if __name__ == "__main__":
    main()
