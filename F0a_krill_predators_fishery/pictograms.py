"""
Pictograms for the F0a diagram: Antarctic krill, five of its predators and a
krill trawler.

Each function returns one pictogram as a shapely geometry, in its own
arbitrary units, with y pointing down and the animal (or the bow) facing
right. A pictogram is a union of smooth outlines, from which thin shapes are
removed to draw the details (eye, mouth, body segments, windows). The holes
are part of the geometry, so a pictogram is filled in a single colour and
whatever lies behind it shows through the details.

The shapes are stylised, not anatomical drawings:

  krill()    Antarctic krill (Euphausia superba)
  whale()    humpback whale (Megaptera novaeangliae)
  seal()     crabeater seal (Lobodon carcinophaga)
  penguin()  Adelie penguin (Pygoscelis adeliae)
  prion()    Antarctic prion (Pachyptila desolata)
  icefish()  mackerel icefish (Champsocephalus gunnari)
  trawler()  stern trawler

They were drawn for this presentation and are not taken from another source.
"""

from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _catmull(p0, p1, p2, p3, n):
    """n points of the Catmull-Rom segment from p1 to p2."""
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    return 0.5 * (
        2 * p1
        + (-p0 + p2) * t
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
        + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
    )


def open_curve(pts, n=20):
    """Smooth open curve through pts."""
    p = np.array(pts, float)
    if len(p) == 2:
        return p
    ext = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = [
        _catmull(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], n)
        for i in range(len(p) - 1)
    ]
    return np.vstack(out + [p[-1:]])


def blob(pts, n=20):
    """Closed shape through pts. A point given as (x, y, 'c') is a sharp corner."""
    corners = [i for i, q in enumerate(pts) if len(q) == 3]
    xy = [(q[0], q[1]) for q in pts]
    if not corners:
        p = np.array(xy, float)
        m = len(p)
        out = [
            _catmull(p[(i - 1) % m], p[i], p[(i + 1) % m], p[(i + 2) % m], n)
            for i in range(m)
        ]
        return Polygon(np.vstack(out)).buffer(0)
    # rotate so the list starts at a corner, then smooth each run
    k = corners[0]
    xy = xy[k:] + xy[:k]
    corners = [c - k for c in corners] + [len(xy)]
    xy = xy + [xy[0]]
    out = []
    for a, b in zip(corners[:-1], corners[1:]):
        out.append(open_curve(xy[a : b + 1], n)[:-1])
    return Polygon(np.vstack(out)).buffer(0)


def stroke(pts, w, smooth=True, cap="round"):
    """Line of width w through pts, as a polygon."""
    c = open_curve(pts) if smooth else np.array(pts, float)
    return LineString(c).buffer(w / 2, cap_style=cap, join_style="round")


def circle(x, y, r):
    return Point(x, y).buffer(r, 48)


def rect(x0, y0, x1, y1):
    return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def soften(g, r):
    """Round convex and concave corners by radius r."""
    return g.buffer(r).buffer(-2 * r).buffer(r)


# ---------------------------------------------------------------------------
# Whale
# ---------------------------------------------------------------------------

def whale():
    """Humpback whale: long flipper, small dorsal fin, throat pleats."""
    body = blob(
        [
            (374, 100),
            (352, 80),
            (318, 68),
            (270, 60),
            (215, 60),
            (165, 68),
            (120, 82),
            (78, 96),
            (44, 100, "c"),
            (30, 86),
            (4, 72, "c"),
            (14, 92),
            (20, 104, "c"),
            (12, 118),
            (4, 136, "c"),
            (30, 122),
            (46, 110, "c"),
            (84, 114),
            (130, 124),
            (185, 136),
            (245, 142),
            (300, 138),
            (342, 126),
            (368, 112),
        ]
    )
    dorsal = blob([(162, 70, "c"), (148, 63), (138, 61, "c"), (134, 71), (124, 82, "c")])
    flipper = blob(
        [
            (284, 122, "c"),
            (262, 150),
            (228, 176),
            (192, 190, "c"),
            (212, 164),
            (232, 140),
            (246, 122, "c"),
        ]
    )
    g = soften(unary_union([body, dorsal, flipper]), 1.5)
    mouth = stroke([(376, 102), (350, 108), (322, 106), (300, 98)], 2.6)
    eye = circle(290, 106, 3.4)
    pleats = [
        stroke([(356, 118), (322, 126), (285, 129)], 2.2),
        stroke([(346, 126), (314, 133), (280, 135)], 2.2),
    ]
    return g - unary_union([mouth, eye, *pleats])


# ---------------------------------------------------------------------------
# Seal
# ---------------------------------------------------------------------------

def seal():
    """Crabeater seal, lying on its belly."""
    body = blob(
        [
            (376, 70),
            (364, 54),
            (342, 44),
            (318, 46),
            (296, 56),
            (262, 56),
            (215, 56),
            (165, 64),
            (118, 78),
            (82, 92),
            (56, 100, "c"),
            (36, 92),
            (10, 86, "c"),
            (24, 102),
            (30, 110, "c"),
            (20, 120),
            (8, 136, "c"),
            (36, 128),
            (60, 122, "c"),
            (100, 126),
            (160, 128),
            (225, 128),
            (280, 124),
            (316, 110),
            (340, 92),
            (362, 82),
        ]
    )
    flipper = blob(
        [
            (296, 112, "c"),
            (286, 136),
            (262, 156),
            (236, 162, "c"),
            (248, 142),
            (256, 120),
            (262, 110, "c"),
        ]
    )
    g = soften(unary_union([body, flipper]), 1.5)
    eye = circle(346, 62, 3.6)
    nose = stroke([(376, 74), (364, 76)], 2.2)
    fl_line = stroke([(292, 114), (272, 126), (258, 142)], 2.2)
    return g - unary_union([eye, nose, fl_line])


# ---------------------------------------------------------------------------
# Penguin
# ---------------------------------------------------------------------------

def penguin():
    """Adelie penguin, standing: white front and white eye ring as holes."""
    body = blob(
        [
            (112, 22),
            (132, 30),
            (142, 44, "c"),
            (172, 56, "c"),
            (142, 63),
            (137, 78),
            (153, 115),
            (165, 165),
            (163, 215),
            (148, 254),
            (138, 266, "c"),
            (140, 273),
            (170, 283, "c"),
            (134, 287),
            (100, 285),
            (78, 277),
            (40, 292, "c"),
            (54, 258),
            (47, 210),
            (47, 160),
            (57, 108),
            (77, 62),
            (91, 34),
        ]
    )
    belly = blob(
        [
            (128, 92),
            (145, 122),
            (156, 166),
            (154, 213),
            (140, 250),
            (118, 267),
            (98, 256),
            (88, 214),
            (88, 166),
            (97, 122),
            (112, 94),
        ]
    )
    flipper = blob(
        [
            (86, 98, "c"),
            (62, 132),
            (40, 172),
            (26, 206, "c"),
            (54, 184),
            (74, 150),
            (84, 118, "c"),
        ]
    )
    eye_ring = circle(124, 46, 7.5) - circle(124, 46, 3.6)
    g = soften(unary_union([body, flipper]), 1.5) - belly - eye_ring
    fl_line = stroke([(83, 122), (72, 152), (54, 182)], 2.4)
    return g - fl_line


# ---------------------------------------------------------------------------
# Prion
# ---------------------------------------------------------------------------

def prion():
    """Antarctic prion in flight: narrow pointed wings, wedge-shaped tail."""
    body = blob(
        [
            (356, 113, "c"),
            (340, 105),
            (326, 98),
            (308, 96),
            (288, 100),
            (252, 101),
            (208, 104),
            (166, 109),
            (140, 113),
            (116, 112, "c"),
            (110, 122, "c"),
            (140, 127),
            (166, 131),
            (208, 135),
            (252, 135),
            (292, 129),
            (322, 123),
            (340, 118),
        ]
    )
    near_wing = blob(
        [
            (278, 103, "c"),
            (272, 78),
            (254, 54),
            (224, 35),
            (184, 21),
            (140, 11),
            (100, 8, "c"),
            (140, 25),
            (178, 42),
            (206, 60),
            (220, 82),
            (224, 105, "c"),
        ]
    )
    far_wing = blob(
        [
            (308, 100, "c"),
            (318, 76),
            (320, 52),
            (310, 32),
            (292, 16, "c"),
            (297, 40),
            (299, 62),
            (293, 82),
            (284, 101, "c"),
        ]
    )
    g = soften(unary_union([body, near_wing, far_wing]), 1.5)
    eye = circle(327, 106, 3.2)
    bill = stroke([(356, 114), (342, 113)], 2.0)
    wing_line = stroke([(270, 104), (246, 110), (222, 108)], 2.2)
    return g - unary_union([eye, bill, wing_line])


# ---------------------------------------------------------------------------
# Icefish
# ---------------------------------------------------------------------------

def icefish():
    """Mackerel icefish: long snout, two dorsal fins, long anal fin."""
    body = blob(
        [
            (394, 84, "c"),
            (368, 74),
            (338, 64),
            (304, 58),
            (250, 56),
            (190, 60),
            (130, 67),
            (84, 74),
            (56, 77, "c"),
            (36, 60),
            (14, 44, "c"),
            (23, 66),
            (27, 80, "c"),
            (23, 94),
            (14, 116, "c"),
            (36, 100),
            (56, 87, "c"),
            (84, 90),
            (130, 96),
            (190, 101),
            (250, 103),
            (304, 100),
            (340, 97),
            (370, 93),
        ]
    )
    fins = unary_union(
        [
            blob([(282, 62, "c"), (268, 36), (258, 22, "c"), (249, 40), (240, 62, "c")]),
            blob([(228, 64, "c"), (216, 42), (206, 33, "c"), (160, 41), (112, 55), (82, 78, "c")]),
            blob([(214, 96, "c"), (204, 116), (194, 125, "c"), (152, 117), (112, 105), (82, 86, "c")]),
            blob([(298, 96, "c"), (290, 116), (272, 132, "c"), (275, 114), (272, 98, "c")]),
        ]
    )
    body = soften(body, 1.3)
    fins = soften(fins - body.buffer(2.6), 1.0)
    eye = circle(340, 76, 6.2) - circle(340, 76, 2.6)
    mouth = stroke([(394, 86), (372, 86), (354, 89)], 2.4)
    gill = stroke([(320, 64), (310, 79), (316, 96)], 2.4)
    pect = stroke([(302, 77), (282, 73), (264, 81), (280, 88), (302, 85)], 2.2)
    return unary_union([body - unary_union([eye, mouth, gill, pect]), fins])


# ---------------------------------------------------------------------------
# Krill
# ---------------------------------------------------------------------------

def krill():
    """Antarctic krill: six thoracic legs, five pairs of swimming legs."""
    body = blob(
        [
            (322, 80, "c"),
            (300, 68),
            (268, 62),
            (236, 62),
            (204, 64),
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
            (144, 100),
            (174, 96),
            (204, 96),
            (240, 100),
            (276, 102),
            (304, 98),
            (318, 90),
        ]
    )
    eye = circle(330, 92, 10.5)
    ant = [
        stroke([(318, 82), (346, 66), (372, 42), (392, 14)], 3.2),
        stroke([(322, 86), (352, 80), (378, 66), (398, 46)], 3.2),
    ]
    # thoracic legs (feeding basket), pointing forward and down
    legs = []
    for i, x in enumerate(np.linspace(304, 236, 6)):
        ln = 30 + 2.5 * i
        legs.append(stroke([(x, 98), (x + 4, 98 + 0.55 * ln), (x + 16, 98 + ln)], 3.0))
    # pleopods (swimming legs) under the abdomen
    top = [(204, 64), (170, 68), (136, 76), (104, 90), (78, 108)]
    bot = [(204, 96), (174, 96), (144, 100), (116, 110), (92, 124)]
    pleo, gaps = [], []
    for i, ((xt, yt), (xb, yb)) in enumerate(zip(top, bot)):
        gaps.append(stroke([(xt + 2, yt - 4), (xb + 2, yb + 4)], 2.6, smooth=False))
        mx, my = xb - 14, yb + (1.5 if i < 2 else 4 + 2.2 * (i - 1))
        pleo.append(
            blob([(mx + 5, my - 2, "c"), (mx + 2, my + 12), (mx - 10, my + 24, "c"), (mx - 6, my + 8), (mx - 5, my - 2, "c")])
        )
    tail_gap = stroke([(60, 120), (72, 142)], 2.6, smooth=False)
    g = soften(unary_union([body, *ant, *legs, *pleo]), 0.8)
    g = g - unary_union([*gaps, tail_gap])
    ring = eye.buffer(2.6) - eye
    g = (g - ring).union(eye) - circle(333, 89, 2.6)
    return g


# ---------------------------------------------------------------------------
# Trawler
# ---------------------------------------------------------------------------

def trawler():
    """Stern trawler with its gantry and trawl warp at the stern, on a wave."""
    hull = Polygon(
        [
            (392, 96),
            (330, 100),
            (322, 114),
            (26, 114),
            (20, 122),
            (34, 158),
            (348, 158),
            (372, 132),
        ]
    )
    house = rect(240, 78, 316, 116)
    bridge = Polygon([(252, 54), (312, 54), (318, 80), (246, 80)])
    funnel = Polygon([(196, 84), (222, 84), (226, 116), (192, 116)])
    mast = unary_union(
        [rect(280, 22, 285, 56), rect(268, 32, 297, 36.5), rect(274, 42, 291, 46)]
    )
    crane = unary_union(
        [
            stroke([(150, 116), (150, 62)], 6, smooth=False, cap="flat"),
            stroke([(150, 64), (196, 46)], 4.5, smooth=False),
            stroke([(196, 46), (196, 70)], 2.2, smooth=False),
        ]
    )
    gantry = unary_union(
        [
            stroke([(52, 116), (66, 56)], 6, smooth=False),
            stroke([(96, 116), (82, 56)], 6, smooth=False),
            stroke([(60, 58), (88, 58)], 6, smooth=False),
            stroke([(58, 86), (90, 86)], 4, smooth=False),
        ]
    )
    warp = stroke([(64, 60), (30, 112), (2, 150)], 2.2, smooth=False)
    ship = soften(unary_union([hull, house, bridge, funnel]), 2.0)
    ship = unary_union([ship, mast, crane, gantry, warp])
    windows = unary_union([rect(258 + 14 * i, 61, 268 + 14 * i, 70) for i in range(4)])
    ports = unary_union([circle(256 + 16 * i, 98, 3.2) for i in range(4)])
    stripe = rect(40, 126, 352, 129.5).intersection(hull.buffer(-5))
    ship = ship - unary_union([windows, ports, stripe])
    xs = np.linspace(-4, 396, 240)
    wave = stroke(
        [(x, 172 + 4.2 * math.sin((x - 10) / 400 * 2 * math.pi * 6.5)) for x in xs],
        5,
        smooth=False,
    )
    return unary_union([ship, wave])
