"""
F0 plot: Antarctic krill between its predators and the fishery.

A diagram, not a data figure. Krill is in the middle. Four of its predators
are on the left (humpback whale, crabeater seal, Adelie penguin, mackerel
icefish) and a krill trawler is on the right. An arrow runs from each of them
to the krill: all five take krill.

The pictograms come from pictograms.py. This script scales them, places them
and draws the arrows. Everything is filled in one colour on a transparent
background; the details of the pictograms are holes.

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
from shapely.geometry import LineString, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

import pictograms


# ---------------------------------------------------------------------------
# Style and layout
# ---------------------------------------------------------------------------
#
# Lengths are in hundredths of an inch, with the origin at the top left and
# y pointing down.

mpl.rcParams.update({
    "figure.figsize": (9.32, 3.74),
})

COLOR = "#222222"

# Width of the krill, and its clearance: the arrows stop on an ellipse this
# far outside its bounding box.
KRILL_WIDTH = 236
KRILL_CLEARANCE = 16

# Predators, top to bottom: pictogram, width or height, right edge, centre y.
# The outer two sit further right than the inner two, so that the four arrows
# have similar lengths.
PREDATORS = (
    (pictograms.whale, {"w": 200}, 232, 47),
    (pictograms.seal, {"w": 190}, 212, 136),
    (pictograms.penguin, {"h": 92}, 212, 229),
    (pictograms.icefish, {"w": 196}, 232, 326),
)

# Trawler: width, distance to the right edge, and the fraction of its height
# (from the top) that is level with the krill, so that the arrow leaves from
# the hull.
TRAWLER_WIDTH = 225
TRAWLER_MARGIN = 6
TRAWLER_LEVEL = 0.70

# Gap between a pictogram and the start of its arrow.
ARROW_GAP_PREDATOR = 14
ARROW_GAP_TRAWLER = 12

# Arrow: shaft width, head length and head width.
ARROW_WIDTH = 3.2
ARROW_HEAD_LENGTH = 15
ARROW_HEAD_WIDTH = 13


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


def put(geom, cy, right=None, cx=None):
    """Move geom so that its centre is at height cy, and its right edge at
    `right` or its centre at `cx`."""
    x0, y0, x1, y1 = geom.bounds
    dx = right - x1 if right is not None else cx - (x0 + x1) / 2
    return affinity.translate(geom, dx, cy - (y0 + y1) / 2)


def arrow(start, end):
    """Arrow from start to end, as a polygon."""
    (x0, y0), (x1, y1) = start, end
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    bx, by = x1 - ux * ARROW_HEAD_LENGTH, y1 - uy * ARROW_HEAD_LENGTH
    shaft = LineString([start, (bx + ux, by + uy)]).buffer(
        ARROW_WIDTH / 2, cap_style="round"
    )
    half = ARROW_HEAD_WIDTH / 2
    head = Polygon([
        (x1, y1),
        (bx - uy * half, by + ux * half),
        (bx + uy * half, by - ux * half),
    ]).buffer(0.8)
    return unary_union([shaft, head])


def on_ellipse(point, centre, rx, ry):
    """Where the segment from point to centre crosses the ellipse of
    half-axes rx and ry around centre."""
    dx, dy = point[0] - centre[0], point[1] - centre[1]
    s = 1 / math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    return (centre[0] + s * dx, centre[1] + s * dy)


def compose(width, height):
    """All the shapes of the diagram, on a canvas of width x height."""
    centre = (width / 2, height / 2)
    krill = put(fit(pictograms.krill(), w=KRILL_WIDTH), centre[1], cx=centre[0])
    x0, y0, x1, y1 = krill.bounds
    rx = (x1 - x0) / 2 + KRILL_CLEARANCE
    ry = (y1 - y0) / 2 + KRILL_CLEARANCE
    shapes = [krill]

    for pictogram, size, right, cy in PREDATORS:
        shapes.append(put(fit(pictogram(), **size), cy, right=right))
        start = (right + ARROW_GAP_PREDATOR, cy)
        shapes.append(arrow(start, on_ellipse(start, centre, rx, ry)))

    trawler = fit(pictograms.trawler(), w=TRAWLER_WIDTH)
    x0, y0, x1, y1 = trawler.bounds
    trawler = affinity.translate(
        trawler,
        width - TRAWLER_MARGIN - x1,
        centre[1] - (y0 + TRAWLER_LEVEL * (y1 - y0)),
    )
    shapes.append(trawler)
    start = (trawler.bounds[0] - ARROW_GAP_TRAWLER, centre[1])
    shapes.append(arrow(start, on_ellipse(start, centre, rx, ry)))

    for shape in shapes:
        x0, y0, x1, y1 = shape.bounds
        if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
            raise ValueError(f"shape outside the canvas: {shape.bounds}")
    return shapes


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def to_patch(geom):
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
        facecolor=COLOR,
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
    for shape in compose(width, height):
        ax.add_patch(to_patch(shape))

    fig.savefig(args.output, dpi=500, transparent=True)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
