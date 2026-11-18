"""
MS1 plot: render the frames of the outcome movie.

One frame per tracking day, from release (frame 0) to the end of tracking
(frame 200). Each frame shows the date, a map and a legend. The map shows, on
the F1 base map:

  - daily GLORYS12 sea-ice concentration above the 15% advance threshold,
  - the shelf and slope shallower than 2000 m, in light gray: the bathymetric
    condition for recruitment success (its complement is M5b),
  - every particle still drifting, in translucent gray,
  - particles whose outcome is decided at sea-ice advance or during the
    calyptopis stages, frozen at their fate position: green for recruitment
    success, which stays; red for M4, M5a and M5b, which fades out over
    FADE_DAYS days so the map stays readable.

Only particles that drift are shown. M1 particles are never spawned, so they
are left out entirely. M6 and censored particles are only classified at the
end of tracking, when the movie ends: they stay gray throughout, so the gray
cloud left on the last frame is the larvae winter sea ice never reached.
Outcome timing otherwise follows the classification exactly, through the
archived fate day. Domain exits are a modelling limitation rather than an
outcome: those particles drift in gray until deleted, then disappear.

The base map reuses the F1 helpers (land, coastline, CCAMLR outlines, domain
boundary) by importing ../F1_domain_map/plot.py, so the two cannot drift
apart. F1's subarea labels, 48.6 split, bathymetry zones, sea-ice climatology
and legends are left out; the legend names the outlines as CCAMLR subareas.
The map is fitted to the domain's bounding box and takes the full width of
the frame.

Reads data/aggregated.nc produced by aggregate.py, and the bathymetry in
../F1_domain_map/data/aggregated.nc for the shelf-slope zone. That bathymetry
is masked to the CCAMLR subareas, so the zone is drawn inside them only, plus
the strip south of the GLORYS12 grid (about 77 deg S) across the domain's
longitudes, which is shelf in front of the Weddell ice shelves.

Usage
-----
    python plot.py                    # all frames into frames/
    python plot.py --frames 0:10      # a range, python slice semantics
    python plot.py --stride 10        # every 10th particle, for quick tests

Frame ranges are independent, so long renders can be split across processes.
Assemble the movie with make_movie.sh.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# F1 helpers, imported by path: the module is named plot.py like this one.
_spec = importlib.util.spec_from_file_location(
    "f1_plot", REPO_ROOT / "F1_domain_map" / "plot.py")
f1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f1)

PROJECTION = f1.PROJECTION
DATA_TRANSFORM = f1.DATA_TRANSFORM


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

# Set after the F1 import, which sets its own figure size.
mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 14,
    "figure.figsize": (4.37, 3.74),
    "legend.labelspacing": 0.3,
})

# 1748 x 1496 px: both even, as H.264 in yuv420p requires.
DPI = 400


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Frame layout, top to bottom: the date, the map, the legend. All in inches.
# The map takes the frame width less a margin on each side, and its height
# follows from the projected aspect of the domain. The three are stacked
# without gaps other than the ones below and centred vertically in the frame.
MARGIN = 0.04                          # left and right of the map
DATE_HEIGHT = 0.30                     # band holding the date
LEGEND_HEIGHT = 0.56                   # band holding the three legend rows
LEGEND_PAD = 0.08                      # between the map and the legend

# Days over which a red particle fades from opaque to invisible.
FADE_DAYS = 5

# Particles.
MARKER_SIZE = 0.23                     # points^2; ~546,000 particles
# Mid gray: darker than the land (0.85) and the shelf-slope zone (~0.90),
# lighter than the black coastline, and translucent so that only dense
# clouds read as solid.
DRIFTING_COLOR = mpl.colors.to_rgba("0.45", alpha=0.12)
SUCCESS_COLOR = mpl.colors.to_rgba("C2", alpha=1.0)
LOST_COLOR = mpl.colors.to_rgba("C3", alpha=1.0)

# Sea ice: transparent at or below the 15% advance threshold. Above it, either
# a gradient from pale to light blue with concentration (SIC_BINARY = False),
# or a single light blue (SIC_BINARY = True), which reads as "ice has arrived"
# in the sense of the advance criterion. Kept light so particles read on top
# of it and distinct from the gray land.
SIC_THRESHOLD = 0.15
SIC_BINARY = True
SIC_CMAP = LinearSegmentedColormap.from_list(
    "ice", [(0.0, "#e6f2fb"), (1.0, "#9cc8e8")])
SIC_CMAP.set_under((0, 0, 0, 0))
SIC_CMAP.set_bad((0, 0, 0, 0))
SIC_BINARY_VALUE = 0.6                 # colormap position used when binary

# Shelf and slope shallower than 2000 m: the bathymetric condition for
# recruitment success. Drawn over the sea ice as a translucent gray, so it
# stays visible under the ice, where it matters, and stays lighter than land
# (0.85) in open water.
HABITAT_DEPTH = 2000.0
HABITAT_COLOR = "0.55"
HABITAT_ALPHA = 0.22
SOUTH_STRIP_POINTS = 1000              # grid points along each parallel

# Text.
LEGEND_LABELS = {
    "drifting": "Drifting larvae",
    "success": "Ready to overwinter",
    "lost": "Did not make it",
    "ice": "Sea ice",
    "habitat": "Shallower than 2000 m",
    "ccamlr": "CCAMLR subareas",
}
# One step below the base size, so that the two columns fit the frame width.
LEGEND_SIZE = "small"
# Legend dots, as a fraction of the legend font size.
LEGEND_DOT = 0.6

# Zorder stack, slotted around F1's: ice and shelf-slope zone under the
# CCAMLR outlines (2), particles above them, all under land (3).
ZORDER_ICE = 1.2
ZORDER_HABITAT = 1.6
ZORDER_DRIFTING = 2.4
ZORDER_LOST = 2.5
ZORDER_SUCCESS = 2.6

AGGREGATED = HERE / "data" / "aggregated.nc"
F1_AGGREGATED = REPO_ROOT / "F1_domain_map" / "data" / "aggregated.nc"
FRAMES_DIR = HERE / "frames"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

class Cohort:
    """Lazy access to the movie aggregation, one day at a time."""

    def __init__(self, path: Path, stride: int):
        # decode_times=False: fate_day carries "days since release" in files
        # written before aggregate.py switched to plain "days", which xarray
        # would otherwise try to parse as a CF time axis.
        self.ds = xr.open_dataset(path, decode_times=False)
        self.stride = stride
        sel = slice(None, None, stride)

        meanings = self.ds["outcome"].attrs["flag_meanings"].split()
        values = np.atleast_1d(self.ds["outcome"].attrs["flag_values"])
        code = dict(zip(meanings, values))
        outcome = self.ds["outcome"].values[sel]

        self.success = outcome == code["success"]
        self.exited = outcome == code["exited_domain"]
        # Never spawned: not drawn at all.
        self.unspawned = outcome == code["killed_M1"]
        # Classified at the end of tracking: drawn as drifting throughout.
        self.no_ice = np.isin(outcome, [code["killed_M6_no_advance"],
                                        code["censored"]])
        # Decided during tracking, drawn red: M4, M5a, M5b.
        self.lost = ~(self.success | self.exited | self.unspawned | self.no_ice)
        self.fate_day = self.ds["fate_day"].values[sel].astype(int)

        # Fate positions are fixed: project them once.
        xy = PROJECTION.transform_points(
            DATA_TRANSFORM,
            self.ds["final_lon"].values[sel].astype(np.float64),
            self.ds["final_lat"].values[sel].astype(np.float64))
        self.fate_xy = xy[:, :2]

        self.n_obs = self.ds.sizes["day"]
        self.release_date = pd.Timestamp(self.ds.attrs["release_date"])
        self.sic_lon = self.ds["sic_lon"].values
        self.sic_lat = self.ds["sic_lat"].values

    def positions(self, day: int, mask: np.ndarray) -> np.ndarray:
        """Projected positions on `day` of the particles selected by `mask`."""
        sel = slice(None, None, self.stride)
        lon = self.ds["lon"].isel(day=day).values[sel][mask]
        lat = self.ds["lat"].isel(day=day).values[sel][mask]
        ok = np.isfinite(lon) & np.isfinite(lat)
        xy = PROJECTION.transform_points(DATA_TRANSFORM,
                                         lon[ok].astype(np.float64),
                                         lat[ok].astype(np.float64))
        return xy[:, :2]

    def sea_ice(self, day: int) -> np.ndarray:
        """Concentration as a fraction, NaN over land."""
        return self.ds["sic"].isel(day=day).values / 100.0


def frame_state(cohort: Cohort, frame: int):
    """
    Which particles are drawn how on a given frame.

    Returns masks for particles drawn at their position of the day (gray),
    particles drawn gray at their final position (M6 whose last valid day
    falls one day before the end), success, and red with their alphas.
    """
    age = frame - cohort.fate_day                     # days since the fate
    moving = ((cohort.exited | cohort.no_ice) & (age <= 0)) | (
        (cohort.success | cohort.lost) & (age < 0))
    # M6 particles carry their position up to their last valid day, usually
    # the final day; a Parcels precision NaN can end it one day early, in
    # which case they are held at that last position rather than vanishing.
    held = cohort.no_ice & (age > 0)
    success = cohort.success & (age >= 0)
    lost = cohort.lost & (age >= 0) & (age < FADE_DAYS)
    lost_alpha = 1.0 - age[lost] / FADE_DAYS
    return moving, held, success, lost, lost_alpha


# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------

def domain_aspect() -> float:
    """Width over height of the domain's bounding box, once projected."""
    n = 200
    lon = np.concatenate([
        np.linspace(f1.LON_MIN, f1.LON_MAX, n), np.full(n, f1.LON_MAX),
        np.linspace(f1.LON_MAX, f1.LON_MIN, n), np.full(n, f1.LON_MIN)])
    lat = np.concatenate([
        np.full(n, f1.LAT_MIN), np.linspace(f1.LAT_MIN, f1.LAT_MAX, n),
        np.full(n, f1.LAT_MAX), np.linspace(f1.LAT_MAX, f1.LAT_MIN, n)])
    xy = PROJECTION.transform_points(DATA_TRANSFORM, lon, lat)
    return float(np.ptp(xy[:, 0]) / np.ptp(xy[:, 1]))


def frame_layout(fig) -> dict:
    """
    Where the date, the map and the legend go, in figure fractions.

    Returns the map rectangle (left, right, bottom, top), the height at which
    the date is centred and the top of the legend.
    """
    width, height = fig.get_size_inches()
    map_width = width - 2 * MARGIN
    map_height = map_width / domain_aspect()
    block = DATE_HEIGHT + map_height + LEGEND_PAD + LEGEND_HEIGHT
    if block > height:
        raise ValueError(f"The date, the map and the legend need {block:.2f} "
                         f"in, the frame is {height:.2f} in high.")
    top = height - 0.5 * (height - block)
    map_top = top - DATE_HEIGHT
    map_bottom = map_top - map_height
    return {
        "map": (MARGIN / width, 1 - MARGIN / width,
                map_bottom / height, map_top / height),
        "date_y": (top - 0.5 * DATE_HEIGHT) / height,
        "legend_top": (map_bottom - LEGEND_PAD) / height,
    }


def add_habitat(ax) -> None:
    """Shelf and slope shallower than HABITAT_DEPTH, as one translucent zone."""
    ds = xr.open_dataset(F1_AGGREGATED)
    depth = ds["bathymetry_masked"].values
    zone = np.where((depth > 0) & (depth < HABITAT_DEPTH), 1.0, np.nan)
    ax.contourf(ds["nav_lon"].values, ds["nav_lat"].values, zone,
                levels=[0.5, 1.5], colors=[HABITAT_COLOR],
                alpha=HABITAT_ALPHA, transform=DATA_TRANSFORM,
                zorder=ZORDER_HABITAT)

    # The GLORYS12 grid stops at about 77 deg S, but the sea continues south,
    # in front of and under the Weddell ice shelves. That strip is shelf, not
    # deep water: fill it with the same zone colour, from the grid's southern
    # edge (so the two fills meet without a gap) to the pole, between the
    # domain's longitudes. It is drawn exactly like the zone above, as a
    # contourf on a lon/lat grid, so cartopy projects both the same way. Land
    # is drawn on top, so only what is not land shows it.
    grid_south = float(np.nanmin(ds["nav_lat"].values))
    strip_lon, strip_lat = np.meshgrid(
        np.linspace(f1.LON_MIN, f1.LON_MAX, SOUTH_STRIP_POINTS),
        np.linspace(-89.99, grid_south, SOUTH_STRIP_POINTS // 10))
    ax.contourf(strip_lon, strip_lat, np.ones_like(strip_lon),
                levels=[0.5, 1.5], colors=[HABITAT_COLOR],
                alpha=HABITAT_ALPHA, transform=DATA_TRANSFORM,
                zorder=ZORDER_HABITAT)


def ice_field(sic: np.ndarray) -> np.ma.MaskedArray:
    """What the ice layer draws: concentration, or a flat value if binary."""
    if SIC_BINARY:
        sic = np.where(sic > SIC_THRESHOLD, SIC_BINARY_VALUE, np.nan)
    return np.ma.masked_invalid(sic)


def add_legend(fig, top: float) -> None:
    """Two columns under the map: the particles, then the map layers."""
    dot_size = LEGEND_DOT * mpl.font_manager.FontProperties(
        size=LEGEND_SIZE).get_size_in_points()

    def dot(color, label):
        return Line2D([], [], linestyle="none", marker="o",
                      markersize=dot_size, markerfacecolor=color,
                      markeredgecolor="none", label=label)

    handles = [
        dot(mpl.colors.to_rgba(DRIFTING_COLOR, 1.0), LEGEND_LABELS["drifting"]),
        dot(SUCCESS_COLOR, LEGEND_LABELS["success"]),
        dot(LOST_COLOR, LEGEND_LABELS["lost"]),
        Patch(facecolor=SIC_CMAP(SIC_BINARY_VALUE if SIC_BINARY else 0.5),
              edgecolor="none", label=LEGEND_LABELS["ice"]),
        Patch(facecolor=HABITAT_COLOR, alpha=HABITAT_ALPHA, edgecolor="none",
              label=LEGEND_LABELS["habitat"]),
        Line2D([], [], color="0.7", linewidth=mpl.rcParams["axes.linewidth"],
               label=LEGEND_LABELS["ccamlr"]),
    ]
    fig.legend(handles=handles, loc="upper center",
               bbox_to_anchor=(0.5, top), ncol=2, frameon=False,
               fontsize=LEGEND_SIZE, borderpad=0, borderaxespad=0,
               handlelength=1.2, handletextpad=0.4, columnspacing=1.0)


def build_figure(cohort: Cohort):
    """Static layers once; returns the figure and the artists updated per frame."""
    fig = plt.figure(dpi=DPI)
    fig.patch.set_facecolor("white")
    layout = frame_layout(fig)
    left, right, bottom, top = layout["map"]
    grid = fig.add_gridspec(1, 1, left=left, right=right,
                            bottom=bottom, top=top)
    ax = fig.add_subplot(grid[0], projection=PROJECTION)
    f1.setup_polar_axes(ax)

    ccamlr = f1.load_ccamlr_geometries()
    f1.add_ccamlr_outlines(ax, ccamlr)
    f1.add_domain_boundary(ax)
    add_habitat(ax)

    ice = ax.pcolormesh(cohort.sic_lon, cohort.sic_lat,
                        ice_field(cohort.sea_ice(0)),
                        cmap=SIC_CMAP, vmin=SIC_THRESHOLD, vmax=1.0,
                        shading="nearest", transform=DATA_TRANSFORM,
                        zorder=ZORDER_ICE, rasterized=True)

    def layer(color, zorder):
        return ax.scatter(np.empty(0), np.empty(0), s=MARKER_SIZE,
                          color=color, linewidths=0, transform=PROJECTION,
                          zorder=zorder, rasterized=True)

    drifting = layer(DRIFTING_COLOR, ZORDER_DRIFTING)
    lost = layer(LOST_COLOR, ZORDER_LOST)
    success = layer(SUCCESS_COLOR, ZORDER_SUCCESS)

    date_text = fig.text(0.5, layout["date_y"], "", ha="center", va="center",
                         fontweight="bold")
    add_legend(fig, layout["legend_top"])

    return fig, {"ice": ice, "drifting": drifting, "lost": lost,
                 "success": success, "date": date_text}


def update(cohort: Cohort, artists: dict, frame: int) -> None:
    day = min(frame, cohort.n_obs - 1)
    date = cohort.release_date + pd.Timedelta(days=day)
    artists["date"].set_text(f"{date.day} {date:%B %Y}")

    sic = cohort.sea_ice(day)
    artists["ice"].set_array(ice_field(sic))

    moving, held, success, lost, lost_alpha = frame_state(cohort, frame)
    artists["drifting"].set_offsets(np.concatenate(
        [cohort.positions(day, moving), cohort.fate_xy[held]]))
    artists["success"].set_offsets(cohort.fate_xy[success])
    artists["lost"].set_offsets(cohort.fate_xy[lost])
    colors = np.tile(LOST_COLOR, (lost_alpha.size, 1))
    colors[:, 3] = lost_alpha
    artists["lost"].set_facecolor(colors)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_frames(spec: str | None, n_frames: int) -> range:
    if not spec:
        return range(n_frames)
    start, _, stop = spec.partition(":")
    return range(n_frames)[slice(int(start) if start else None,
                                 int(stop) if stop else None)]


def main():
    parser = argparse.ArgumentParser(
        description="Render the frames of the outcome movie.")
    parser.add_argument("--frames", help="frame range, e.g. 0:50 (default: all)")
    parser.add_argument("--stride", type=int, default=1,
                        help="draw every Nth particle (default 1, all)")
    parser.add_argument("--data", type=Path, default=AGGREGATED)
    parser.add_argument("--out", type=Path, default=FRAMES_DIR)
    args = parser.parse_args()

    if not args.data.exists():
        raise FileNotFoundError(f"{args.data} not found. Run aggregate.py "
                                f"on the HPC first and copy it here.")

    cohort = Cohort(args.data, args.stride)
    n_frames = cohort.n_obs
    frames = parse_frames(args.frames, n_frames)

    fig, artists = build_figure(cohort)
    args.out.mkdir(parents=True, exist_ok=True)
    for frame in frames:
        update(cohort, artists, frame)
        path = args.out / f"frame_{frame:03d}.png"
        fig.savefig(path, dpi=DPI)
        print(f"Wrote {f1.display_path(path)}")
    plt.close(fig)


if __name__ == "__main__":
    main()
