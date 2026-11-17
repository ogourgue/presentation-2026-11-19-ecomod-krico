"""
F5 plot: destination maps by fate.

Reads data/aggregated.nc and produces destination_maps.png:
  - 2 × 3 grid of polar-stereographic maps, one panel per outcome.
  - Success in top-left, then five killed_M* panels, row by row.
  - Two colormaps echoing F3: Greens (success), Reds (5 mortality).
  - Two shared colorbars at the bottom.

Identical layout to F4. The only difference is the input data: the
density grids in data/aggregated.nc reflect fate positions
(final_lon / final_lat) rather than release positions.

Censored particles are folded into killed_M6_no_advance at plot time
(consistent with F3): they share the same end-of-tracking, no-advance
condition, with "censored" marking only the subset whose classification
is provisional (rising SIC at cutoff).
"""

from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.ticker import MaxNLocator
from shapely.geometry import LineString
from shapely.ops import unary_union


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 14,
    "figure.figsize": (9.32, 3.74),
})

# Layout, in inches. A strip at the bottom of the figure is reserved for the
# colorbars; the panels fill what remains, at the projected aspect of the
# domain, and the panel block is centred horizontally.
MARGIN = 0.04           # blank margin on the left, right and top
PANEL_GAP = 0.05        # between neighbouring panels
CBAR_STRIP = 0.76       # colorbars with their tick labels and axis labels
CBAR_PAD = 0.07         # between the bottom row and the colorbars
CBAR_HEIGHT = 0.12
CBAR_WIDTH = 3.2


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Domain extent for cropping the map (matches the aggregation grid).
LON_MIN, LON_MAX = -115.0, 40.0
LAT_MIN, LAT_MAX = -78.0, -40.0

# Panels: outcome name -> (row, col) in the 2 × 3 grid.
# Success top-left; killed_M* in time-of-action order, row by row.
N_ROWS, N_COLS = 2, 3
PANEL_LAYOUT = [
    ("success",                (0, 0)),
    ("killed_M1",              (0, 1)),
    ("killed_M4",              (0, 2)),
    ("killed_M5_no_FIV",       (1, 0)),
    ("killed_M5_not_on_shelf", (1, 1)),
    ("killed_M6_no_advance",   (1, 2)),
]

# Panel labels: plain-English name first, M-code in parentheses (the same
# labels as in the F3 legend).
PANEL_LABELS = {
    "success":                "Recruitment success",
    "killed_M1":              "Ice at spawning (M1)",
    "killed_M4":              "Calyptopis starvation (M4)",
    "killed_M5_no_FIV":       "Under-developed (M5a)",
    "killed_M5_not_on_shelf": "Off-shelf (M5b)",
    "killed_M6_no_advance":   "No winter ice (M6)",
}

# Color group per outcome; determines colormap and shared scale.
COLOR_GROUP = {
    "success":                "success",
    "killed_M1":              "killed",
    "killed_M4":              "killed",
    "killed_M5_no_FIV":       "killed",
    "killed_M5_not_on_shelf": "killed",
    "killed_M6_no_advance":   "killed",
}

CMAPS = {
    "success": "Greens",
    "killed":  "Reds",
}

# Colorbar labels.
GROUP_LABELS = {
    "success": "Recruitment success",
    "killed":  "Mortality",
}

# Percentile used to set per-group vmax. Clipping at the 99th percentile
# brightens the bulk of the signal at the cost of saturating a few hotspot
# cells.
COLOR_PERCENTILE = 99.0

# Latitude split for 48.6 (consistent with F1 and the F4/F5 ccamlr_summary
# scripts): subarea 48.6 is reported as two halves split at 60°S.
SPLIT_LAT_486 = -60.0

# Number of points used to densify the 60°S divider line so it follows the
# parallel as a smooth curve when rendered in South Polar Stereographic.
N_DIVIDER_POINTS = 200

# Cartopy projection (matches F1).
PROJECTION = ccrs.SouthPolarStereo(central_longitude=-37.5)
DATA_TRANSFORM = ccrs.PlateCarree()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_legend_color(rc_key: str, axes_attr: str) -> str:
    """Resolve matplotlib's 'inherit' sentinel for legend colors."""
    val = mpl.rcParams[rc_key]
    if val == "inherit":
        return mpl.rcParams[axes_attr]
    return val


def make_label_bbox():
    """Bbox style matching the legend frame (white fill, gray border, opaque)."""
    return dict(
        boxstyle="round",
        facecolor=resolve_legend_color("legend.facecolor", "axes.facecolor"),
        edgecolor=resolve_legend_color("legend.edgecolor", "axes.edgecolor"),
        linewidth=mpl.rcParams["axes.linewidth"],
    )


def add_panel_label(ax, fate_name: str):
    """
    Add a framed label with the fate name in the upper-right corner of the
    panel, at a fixed offset from the corner.

    The label is one size down from the base font, so that it stays in the
    strip north of the CCAMLR subareas and covers no part of them.
    """
    ax.annotate(
        fate_name,
        xy=(1, 1), xycoords="axes fraction",
        xytext=(-7, -7), textcoords="offset points",
        ha="right", va="top",
        fontsize="small",
        bbox=make_label_bbox(),
        zorder=10,
    )


def setup_polar_axes(ax):
    """Configure a polar-stereographic axis with land + coastline.

    Zorder stack (bottom to top):
      data (1) < CCAMLR + domain boundaries (2) < land (3) <
      coastlines (4) < axis spines (5) < panel labels (10)
    """
    land = cfeature.NaturalEarthFeature(
        "physical", "land", "50m", facecolor="0.85", edgecolor="none"
    )
    ax.add_feature(land, zorder=3)
    ax.coastlines(resolution="50m", linewidth=mpl.rcParams["axes.linewidth"], zorder=4)
    # Crop to the domain extent.
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=DATA_TRANSFORM)
    # Push axis spines above land/coastlines so the panel border is never
    # covered by features that touch or cross it.
    for spine in ax.spines.values():
        spine.set_zorder(5)


def load_ccamlr_geometries() -> gpd.GeoDataFrame:
    """Load CCAMLR statistical area polygons for the project domain."""
    repo_root = Path(__file__).resolve().parent.parent
    shp_path = repo_root / "shared" / "ccamlr-data" / "CCAMLR_ASD_EPSG4326.shp"
    if not shp_path.exists():
        raise FileNotFoundError(f"CCAMLR shapefile not found: {shp_path}")
    ccamlr = gpd.read_file(shp_path)
    areas = ["48.1", "48.2", "48.3", "48.4", "48.5", "48.6", "88.3"]
    return ccamlr[ccamlr["GAR_Long_L"].isin(areas)]


def add_486_split_line(ax, ccamlr: gpd.GeoDataFrame) -> None:
    """
    Draw a dotted gray line at 60°S inside the 48.6 polygon, marking the
    split between 48.6N and 48.6S used in the F4/F5 spatial analyses
    (consistent with F1).

    The line is densified (N_DIVIDER_POINTS along the lon span) so that
    when rendered on the South Polar Stereographic projection it follows
    the curved 60°S parallel rather than a chord. It is then clipped to
    the 48.6 polygon so it does not extend past the subarea boundary.
    Dotted style distinguishes this internal subdivision from the dashed
    style used for the external computational domain boundary.
    """
    rows = ccamlr[ccamlr["GAR_Long_L"] == "48.6"]
    if rows.empty:
        return
    geom_486 = unary_union(rows.geometry.values)

    # Build a densified horizontal line at 60°S spanning the full lon range
    # of 48.6, with a small pad so clipping by the polygon does not miss
    # the polygon boundary.
    minx, _, maxx, _ = geom_486.bounds
    pad = 1.0
    lons = np.linspace(minx - pad, maxx + pad, N_DIVIDER_POINTS)
    coords = list(zip(lons, np.full_like(lons, SPLIT_LAT_486)))
    full_line = LineString(coords)

    # Clip to the 48.6 polygon. The result may be a MultiLineString if the
    # polygon is multi-part or non-convex (the line exits and re-enters).
    clipped = full_line.intersection(geom_486)
    if clipped.is_empty:
        return

    if hasattr(clipped, "geoms"):
        segments = list(clipped.geoms)
    else:
        segments = [clipped]
    for seg in segments:
        if not isinstance(seg, LineString):
            continue
        xs, ys = seg.xy
        ax.plot(
            list(xs), list(ys),
            color="0.7",
            linestyle=":",
            linewidth=mpl.rcParams["axes.linewidth"],
            transform=DATA_TRANSFORM,
            zorder=2,
        )


def panel_aspect() -> float:
    """
    Width / height of a map panel: the aspect of the domain's bounding box
    in the map projection, computed the way GeoAxes.set_extent does.
    """
    outline = LineString([
        (LON_MIN, LAT_MIN), (LON_MAX, LAT_MIN), (LON_MAX, LAT_MAX),
        (LON_MIN, LAT_MAX), (LON_MIN, LAT_MIN),
    ])
    x_min, y_min, x_max, y_max = PROJECTION.project_geometry(
        outline, DATA_TRANSFORM
    ).bounds
    return (x_max - x_min) / (y_max - y_min)


def add_overlays(ax, ccamlr: gpd.GeoDataFrame) -> None:
    """Add CCAMLR area outlines (plain) and model domain boundary (dashed).

    Both are drawn above data but below continents (zorder=2).
    """
    # CCAMLR area boundaries: plain light-gray lines.
    for _, row in ccamlr.iterrows():
        ax.add_geometries(
            [row.geometry],
            crs=DATA_TRANSFORM,
            facecolor="none",
            edgecolor="0.7",
            linewidth=mpl.rcParams["axes.linewidth"],
            zorder=2,
        )

    # 48.6 split at 60°S: dotted light-gray line marking the 48.6N / 48.6S
    # boundary used in the spatial analyses (consistent with F1).
    add_486_split_line(ax, ccamlr)

    # Model domain boundary: dashed light-gray, densified for smooth polar curves.
    n = 100
    lon_boundary = np.concatenate([
        np.linspace(LON_MIN, LON_MAX, n),
        np.full(n, LON_MAX),
        np.linspace(LON_MAX, LON_MIN, n),
        np.full(n, LON_MIN),
    ])
    lat_boundary = np.concatenate([
        np.full(n, LAT_MIN),
        np.linspace(LAT_MIN, LAT_MAX, n),
        np.full(n, LAT_MAX),
        np.linspace(LAT_MAX, LAT_MIN, n),
    ])
    ax.plot(
        lon_boundary, lat_boundary,
        color="0.7",
        linestyle="--",
        linewidth=mpl.rcParams["axes.linewidth"],
        transform=DATA_TRANSFORM,
        zorder=2,
    )


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

def plot(aggregated_path: Path, out_path: Path) -> None:
    ds = xr.open_dataset(aggregated_path)
    counts = ds["counts"].values                            # (outcome, lat, lon)
    lon_centers = ds["lon"].values
    lat_centers = ds["lat"].values
    outcome_names = list(ds["outcome"].values.astype(str))

    # Fold censored into killed_M6_no_advance at the count level (consistent
    # with F3 and F4). Then renormalize density within each outcome so each
    # panel still sums to 1.
    censored_idx = outcome_names.index("censored")
    m6_idx = outcome_names.index("killed_M6_no_advance")
    counts = counts.copy()
    counts[m6_idx] = counts[m6_idx] + counts[censored_idx]
    counts[censored_idx] = 0

    totals = counts.sum(axis=(1, 2)).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        density = np.where(
            totals[:, None, None] > 0,
            counts / totals[:, None, None],
            0.0,
        ).astype(np.float32)

    # Cell edges for pcolormesh.
    dlon = lon_centers[1] - lon_centers[0]
    dlat = lat_centers[1] - lat_centers[0]
    lon_edges = np.concatenate([lon_centers - dlon / 2, [lon_centers[-1] + dlon / 2]])
    lat_edges = np.concatenate([lat_centers - dlat / 2, [lat_centers[-1] + dlat / 2]])

    # ------------------------------------------------------------------
    # Compute a single shared vmax across all 6 panels, using the 99th
    # percentile of all nonzero density cells pooled together.
    # Both colormaps use the same numeric scale, so a given hue intensity
    # means the same density everywhere in the figure.
    # ------------------------------------------------------------------
    panel_indices = [outcome_names.index(name) for name, _ in PANEL_LAYOUT]
    pooled = np.concatenate([
        density[idx][density[idx] > 0].ravel()
        for idx in panel_indices
    ])
    if pooled.size == 0:
        raise RuntimeError("All panels are empty.")
    shared_vmax = float(np.percentile(pooled, COLOR_PERCENTILE))
    print(f"Shared vmax (P{COLOR_PERCENTILE:.0f} of all nonzero cells): {shared_vmax:.4e}")
    group_max = {"success": shared_vmax, "killed": shared_vmax}

    # ------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------
    # Panels and colorbars are positioned explicitly, in inches from the
    # top-left corner of the figure, then converted to figure fractions.
    fig = plt.figure()
    fig_width, fig_height = fig.get_size_inches()
    aspect = panel_aspect()
    panel_width = min(
        (fig_width - 2 * MARGIN - (N_COLS - 1) * PANEL_GAP) / N_COLS,
        aspect * (fig_height - MARGIN - CBAR_STRIP - (N_ROWS - 1) * PANEL_GAP) / N_ROWS,
    )
    panel_height = panel_width / aspect
    block_width = N_COLS * panel_width + (N_COLS - 1) * PANEL_GAP
    block_left = (fig_width - block_width) / 2

    def panel_rect(row: int, col: int) -> list[float]:
        left = block_left + col * (panel_width + PANEL_GAP)
        top = MARGIN + row * (panel_height + PANEL_GAP)
        return [
            left / fig_width,
            1 - (top + panel_height) / fig_height,
            panel_width / fig_width,
            panel_height / fig_height,
        ]

    # ------------------------------------------------------------------
    # Load CCAMLR area geometries once (shared across panels).
    # ------------------------------------------------------------------
    ccamlr = load_ccamlr_geometries()

    # Track an example mappable per group for the colorbars.
    group_mappable = {}

    for name, (row, col) in PANEL_LAYOUT:
        idx = outcome_names.index(name)
        group = COLOR_GROUP[name]
        cmap = CMAPS[group]
        vmax = group_max[group]

        ax = fig.add_axes(panel_rect(row, col), projection=PROJECTION)
        setup_polar_axes(ax)

        # Mask cells with zero density so the white end of the colormap
        # (≈ background) is not drawn over the land.
        d = density[idx]
        d_masked = np.where(d > 0, d, np.nan)

        mappable = ax.pcolormesh(
            lon_edges, lat_edges, d_masked,
            cmap=cmap,
            vmin=0.0, vmax=vmax,
            transform=DATA_TRANSFORM,
            shading="flat",
            zorder=1,
        )
        group_mappable.setdefault(group, mappable)

        add_overlays(ax, ccamlr)
        add_panel_label(ax, PANEL_LABELS[name])

    # ------------------------------------------------------------------
    # Two colorbars below the bottom row: Greens (success) centred in the
    # left half of the figure, Reds (mortality) centred in the right half.
    # ------------------------------------------------------------------
    cbar_top = MARGIN + N_ROWS * panel_height + (N_ROWS - 1) * PANEL_GAP + CBAR_PAD
    for j, group in enumerate(("success", "killed")):
        centre = (j + 0.5) * fig_width / 2
        cax = fig.add_axes([
            (centre - CBAR_WIDTH / 2) / fig_width,
            1 - (cbar_top + CBAR_HEIGHT) / fig_height,
            CBAR_WIDTH / fig_width,
            CBAR_HEIGHT / fig_height,
        ])
        cb = fig.colorbar(group_mappable[group], cax=cax, orientation="horizontal")
        cb.set_label(f"{GROUP_LABELS[group]} density")
        # Ticks on multiples of 1, 2 or 5, so the labels stay short and
        # clear of each other.
        cb.locator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
        cb.update_ticks()
        # Force scientific notation with the multiplier on the right of the
        # axis (offset text), and shrink it so it doesn't collide with the
        # axis label below.
        cb.ax.ticklabel_format(axis="x", style="sci", scilimits=(-3, 3))
        cb.ax.xaxis.get_offset_text().set_size("smaller")

    fig.savefig(out_path, dpi=500)
    plt.close(fig)
    print(f"Wrote {out_path}")


def main():
    here = Path(__file__).resolve().parent
    aggregated_path = here / "data" / "aggregated.nc"
    out_path = here / "destination_maps.png"

    if not aggregated_path.exists():
        raise FileNotFoundError(f"Aggregated file not found: {aggregated_path}")

    plot(aggregated_path, out_path)


if __name__ == "__main__":
    main()