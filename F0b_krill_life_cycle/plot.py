"""
F0b plot: the first months of the life of Antarctic krill, as the model sees
them.

A diagram, not a data figure. Time runs from left to right, from spawning in
summer to the first winter, and depth from the sea surface at the top to the
seabed at the bottom. Neither is to scale.

Sea ice is at both ends of the surface: it retreats before spawning and
advances again in winter. Below the spawning adult the seabed is the
continental slope; below the winter sea ice it is the shelf and slope, where
larvae must be when sea ice advances. Between the two the water is too deep
for the seabed to show.

Two colours separate what the model simulates from what it does not:

  grey   what comes before the simulation: the spawning adult, the eggs that
         sink, the nauplius that swims back up, their path (dashed) and its
         duration;
  blue   the drift with the currents that the model simulates, from the first
         calyptopis stage to the furcilia stages that can overwinter under
         sea ice. The larvae on that path and their names are dark grey.

The adult krill comes from the pictograms of the F0 diagram, the larvae from
larvae.py. This script scales them, places them and draws the rest, on a
transparent background.

Inputs:  none
Output:  krill_life_cycle.png
"""

from __future__ import annotations

import argparse
import math
import sys
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "F0_krill_predators_fishery"))
import pictograms  # noqa: E402
from pictograms import blob, open_curve, stroke  # noqa: E402

import larvae  # noqa: E402


# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------
#
# Time between spawning and the first calyptopis stage, in days: the eggs sink,
# hatch at depth and the nauplii swim back up. The model does not simulate it
# and starts 24 days after spawning (23 to 26 days in Thorpe et al., 2019).

DESCENT_ASCENT_DAYS = 24


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
SIMULATED = "#4A86E8"
NOT_SIMULATED = "#999999"
ICE_COLOR = "#C9DAF8"
SEABED_COLOR = "#D9D9D9"

# Depth of the sea surface, of the drifting larvae and of their names.
SURFACE = 50
LANE = 112
NAMES = 82

# Sea ice: x-range of the summer slab (left) and of the winter slab (right).
ICE_SUMMER = (-12, 132)
ICE_WINTER = (700, 944)

# Seabed: the slope under the spawning adult, then the shelf and slope under
# the winter sea ice. Both run off the bottom of the canvas.
SLOPE = [(-5, 262), (90, 280), (200, 304), (310, 330), (400, 356), (470, 380)]
SHELF = [(628, 380), (690, 338), (742, 276), (792, 232), (850, 212), (937, 204)]

# Stages: width (or height) and centre.
ADULT = ({"w": 150}, (232, 98))
NAUPLIUS = ({"h": 30}, (340, 226))
CALYPTOPIS = ({"w": 50}, (404, LANE))
FURCILIA_EARLY = ({"w": 62}, (592, LANE))
FURCILIA_LATE = ({"w": 88}, (822, LANE))
EGG_WIDTH = 9
EGGS = ((206, 150), (206, 214), (262, 276))

# Path of the eggs and of the nauplius, in four pieces that leave room for the
# pictograms, and the arrowheads on it (x, y, direction in degrees).
PATH = (
    [(206, 160), (206, 204)],
    [(206, 224), (208, 250), (228, 272), (252, 276)],
    [(272, 276), (310, 272), (334, 256), (340, 246)],
    [(340, 206), (341, 160), (354, 132), (374, 118)],
)
PATH_HEADS = ((206, 196, 90), (340.5, 176, -90))

# Drift: x-range of the two arrows, between the larvae.
DRIFT = ((438, 552), (632, 768))
DRIFT_WIDTH = 2.0
HEAD_WIDTH = 9
HEAD_LENGTH = 11


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


def put(geom, cx, cy):
    """Move geom so that its centre is at (cx, cy)."""
    x0, y0, x1, y1 = geom.bounds
    return affinity.translate(geom, cx - (x0 + x1) / 2, cy - (y0 + y1) / 2)


def place(pictogram, spec):
    size, centre = spec
    return put(fit(pictogram, **size), *centre)


def arrow(x_start, x_end, y):
    """Thin horizontal arrow at depth y, pointing right."""
    x_base = x_end - HEAD_LENGTH
    shaft = Polygon([
        (x_start, y - DRIFT_WIDTH / 2),
        (x_base + 1, y - DRIFT_WIDTH / 2),
        (x_base + 1, y + DRIFT_WIDTH / 2),
        (x_start, y + DRIFT_WIDTH / 2),
    ])
    head = Polygon([
        (x_end, y),
        (x_base, y - HEAD_WIDTH / 2),
        (x_base, y + HEAD_WIDTH / 2),
    ])
    return unary_union([shaft, head])


def arrowhead(x, y, angle, size=6):
    """Small arrowhead at (x, y), pointing in the direction `angle`."""
    tri = Polygon([(size, 0), (-0.5 * size, -0.6 * size), (-0.5 * size, 0.6 * size)])
    return affinity.translate(affinity.rotate(tri, angle, origin=(0, 0)), x, y)


def ice(x0, x1, seed):
    """Slab of sea ice between x0 and x1, floating at the surface, with a
    slightly uneven outline."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, 9)
    top = [(x, SURFACE - 13 + rng.uniform(-2.5, 2.5)) for x in xs]
    bottom = [(x, SURFACE + 14 + rng.uniform(-3.5, 3.5)) for x in xs[::-1]]
    return blob(top + bottom)


def seabed(profile, height):
    """Seabed below a profile, down to well under the canvas."""
    curve = [tuple(p) for p in open_curve(profile)]
    floor = height + 40
    return Polygon([(curve[0][0], floor), *curve, (curve[-1][0], floor)])


def surface(x0, x1):
    """Wavy sea surface between x0 and x1."""
    xs = np.linspace(x0, x1, 200)
    return stroke(
        [(x, SURFACE + 2.2 * math.sin((x - x0) / (x1 - x0) * 2 * math.pi * 9)) for x in xs],
        2.2,
        smooth=False,
    )


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
        default=Path(__file__).parent / "krill_life_cycle.png",
    )
    args = parser.parse_args()

    fig = plt.figure()
    width, height = (100 * v for v in fig.get_size_inches())
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    canvas = Polygon([(0, 0), (width, 0), (width, height), (0, height)])

    def draw(geom, color):
        ax.add_patch(to_patch(geom.intersection(canvas), color))

    # Seabed, sea ice and the sea surface between the two slabs.
    for profile in (SLOPE, SHELF):
        draw(seabed(profile, height), SEABED_COLOR)
    draw(ice(*ICE_SUMMER, seed=3), ICE_COLOR)
    draw(ice(*ICE_WINTER, seed=5), ICE_COLOR)
    draw(surface(ICE_SUMMER[1], ICE_WINTER[0]), COLOR)

    # Before the simulation: adult, eggs, nauplius and their path.
    draw(place(pictograms.krill(), ADULT), NOT_SIMULATED)
    draw(place(larvae.nauplius(), NAUPLIUS), NOT_SIMULATED)
    for centre in EGGS:
        draw(place(larvae.egg(), ({"w": EGG_WIDTH}, centre)), NOT_SIMULATED)
    for piece in PATH:
        curve = open_curve(piece)
        ax.plot(
            curve[:, 0], curve[:, 1],
            color=NOT_SIMULATED, lw=1.4, dashes=(3, 2.5), solid_capstyle="butt",
        )
    for x, y, angle in PATH_HEADS:
        draw(arrowhead(x, y, angle), NOT_SIMULATED)

    # The simulation: the larvae and their drift.
    draw(place(larvae.calyptopis(), CALYPTOPIS), COLOR)
    draw(place(larvae.furcilia(pleopods=2), FURCILIA_EARLY), COLOR)
    draw(place(larvae.furcilia(pleopods=5), FURCILIA_LATE), COLOR)
    for x_start, x_end in DRIFT:
        draw(arrow(x_start, x_end, LANE), SIMULATED)

    # Labels.
    def text(x, y, s, color=COLOR, ha="center"):
        ax.text(x, y, s, color=color, ha=ha, va="center")

    text(8, 18, "Sea ice retreats", ha="left")
    text(width - 8, 18, "Sea ice advances", ha="right")
    text(196, 150, "Spawning", NOT_SIMULATED, ha="right")
    text(217, 214, "Egg", NOT_SIMULATED, ha="left")
    text(359, 226, "Nauplius", NOT_SIMULATED, ha="left")
    text(273, 190, f"{DESCENT_ASCENT_DAYS} days", NOT_SIMULATED)
    text(CALYPTOPIS[1][0], NAMES, "Calyptopis I-III")
    text(FURCILIA_EARLY[1][0], NAMES, "Furcilia I-III")
    text(FURCILIA_LATE[1][0], NAMES, "Furcilia IV-VI")
    text(596, 148, "Drift with the currents", SIMULATED)
    text(14, 344, "Slope", ha="left")
    text(width - 14, 344, "Shelf and slope", ha="right")

    fig.savefig(args.output, dpi=500, transparent=True)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
