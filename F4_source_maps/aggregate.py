"""
F4 aggregation: per-outcome 2D source-position density.

Reads per-particle recruitment outcomes from all cohort files in the
recruitment data directory. For each particle, takes its release_lon /
release_lat and bins onto a regular 1° × 1° lon/lat grid, separately
for each outcome category.

Output is normalized within each outcome (densities sum to 1 across cells
for each outcome): "of all particles that ended in this fate, this is the
fractional spatial source distribution."

Inputs:  $KRICO_POST/recruitment/data/YYYY_MM_DD.nc (3848 files), extracted
         from version 2.0.0 of the KRICO Recruitment Outcomes Dataset
         (1994-2025), https://doi.org/10.5281/zenodo.22548763
Output:  data/aggregated.nc

Every cohort file is checked against that version before it is counted; the
script stops at the first file from another version.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import numpy as np
import xarray as xr


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Input dataset. The DOI is the one of version 2.0.0 itself, not the DOI of
# the dataset as a whole, so it keeps pointing at these files when later
# versions are published.
DATASET_NAME = "KRICO Recruitment Outcomes Dataset (1994-2025)"
DATASET_VERSION = "2.0.0"
DATASET_DOI = "10.5281/zenodo.22548763"

# Global attributes by which the version of a cohort file is recognised
# (see check_dataset_version).
V2_ATTRIBUTES = ("m1_spawning_offset_days", "m1_spawning_date", "m1_sic_source")
LATER_ATTRIBUTES = ("sic_source", "trajectory_sic_source")
M1_SPAWNING_OFFSET_DAYS = 24

# Outcome integer flags from the recruitment pipeline (CF flag values).
OUTCOME_NAMES = (
    "success",                 # 0
    "censored",                # 1
    "killed_M1",               # 2
    "killed_M4",               # 3
    "killed_M5_no_FIV",        # 4
    "killed_M5_not_on_shelf",  # 5
    "killed_M6_no_advance",    # 6
    "exited_domain",           # 7
)
N_OUTCOMES = len(OUTCOME_NAMES)

# 1° × 1° lon/lat grid covering the KRICO domain with a small buffer.
# Domain bounds (from methodology / domain map): 115°W to 40°E, 78°S to 40°S.
LON_MIN, LON_MAX = -115.0, 40.0
LAT_MIN, LAT_MAX = -78.0, -40.0
DLON = DLAT = 1.0


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

COHORT_FILENAME_RE = re.compile(r"^(\d{4})_(\d{2})_(\d{2})\.nc$")


def find_cohort_files(data_dir: Path) -> list[Path]:
    out = []
    for path in sorted(data_dir.iterdir()):
        if COHORT_FILENAME_RE.match(path.name):
            out.append(path)
    return out


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate(data_dir: Path) -> xr.Dataset:
    """
    Walk all cohort files and accumulate per-outcome counts on the lon/lat grid.

    Returns a dataset with dimensions (outcome, lat, lon) containing both
    raw counts and within-outcome normalized density.
    """
    # Cell edges (n+1) and centers (n).
    lon_edges = np.arange(LON_MIN, LON_MAX + DLON, DLON)
    lat_edges = np.arange(LAT_MIN, LAT_MAX + DLAT, DLAT)
    lon_centers = (lon_edges[:-1] + lon_edges[1:]) / 2.0
    lat_centers = (lat_edges[:-1] + lat_edges[1:]) / 2.0
    n_lon = len(lon_centers)
    n_lat = len(lat_centers)

    counts = np.zeros((N_OUTCOMES, n_lat, n_lon), dtype=np.int64)

    files = find_cohort_files(data_dir)
    if not files:
        raise FileNotFoundError(f"No cohort files found in {data_dir}")

    print(f"Found {len(files)} cohort files in {data_dir}")
    print(f"Grid: lon {LON_MIN}..{LON_MAX} ({n_lon} cells), "
          f"lat {LAT_MIN}..{LAT_MAX} ({n_lat} cells)")

    for n, path in enumerate(files, start=1):
        with xr.open_dataset(path) as ds:
            check_dataset_version(ds, path)
            outcome = ds["outcome"].values
            release_lon = ds["release_lon"].values
            release_lat = ds["release_lat"].values

        # Drop particles with NaN release positions (should not happen, but safe).
        valid = ~(np.isnan(release_lon) | np.isnan(release_lat))

        # Bin separately per outcome.
        for code in range(N_OUTCOMES):
            mask = valid & (outcome == code)
            if not mask.any():
                continue
            h, _, _ = np.histogram2d(
                release_lat[mask],
                release_lon[mask],
                bins=[lat_edges, lon_edges],
            )
            counts[code] += h.astype(np.int64)

        if n % 200 == 0:
            print(f"  processed {n} / {len(files)}")

    print("Done.")

    # Normalize within each outcome: density sums to 1 per outcome.
    totals = counts.sum(axis=(1, 2)).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        density = np.where(
            totals[:, None, None] > 0,
            counts / totals[:, None, None],
            0.0,
        ).astype(np.float32)

    ds_out = xr.Dataset(
        data_vars={
            "counts": (
                ("outcome", "lat", "lon"),
                counts,
                {"long_name": "particle count per outcome per 1° × 1° release-position cell"},
            ),
            "density": (
                ("outcome", "lat", "lon"),
                density,
                {
                    "long_name": "fraction of particles of given outcome released in this cell",
                    "description": "Sums to 1 across (lat, lon) for each outcome.",
                },
            ),
            "total": (
                ("outcome",),
                totals.astype(np.int64),
                {"long_name": "total particles in each outcome category"},
            ),
        },
        coords={
            "outcome": ("outcome", np.array(OUTCOME_NAMES)),
            "lat": ("lat", lat_centers.astype(np.float32),
                    {"units": "degrees_north", "long_name": "release latitude (cell center)"}),
            "lon": ("lon", lon_centers.astype(np.float32),
                    {"units": "degrees_east", "long_name": "release longitude (cell center)"}),
        },
        attrs={
            "title": "F4 source maps by fate — climatological aggregation",
            "description": (
                "Per-outcome density of release positions on a 1° × 1° lon/lat grid, "
                "aggregated over all 32 spawning years and all release dates."
            ),
            "grid_lon_min": LON_MIN,
            "grid_lon_max": LON_MAX,
            "grid_lat_min": LAT_MIN,
            "grid_lat_max": LAT_MAX,
            "grid_resolution_deg": DLON,
        },
    )
    return ds_out


# ---------------------------------------------------------------------------
# Dataset version check
# ---------------------------------------------------------------------------

def check_dataset_version(ds: xr.Dataset, path: Path) -> None:
    """
    Stop unless a cohort file comes from version 2.0.0 of the dataset.

    The files carry no version number. The version is recognised from the
    global attributes written by the pipeline that produced them
    (krico-post-production):

      - version 2.0.0 files carry the three M1 provenance attributes, with
        M1 evaluated 24 days before release;
      - version 1.0.0 files carry none of them;
      - files written by later versions of the pipeline (from October 2026)
        also carry sic_source and trajectory_sic_source.
    """
    missing = [name for name in V2_ATTRIBUTES if name not in ds.attrs]
    later = [name for name in LATER_ATTRIBUTES if name in ds.attrs]

    if missing:
        reason = (f"it lacks the global attribute(s) {', '.join(missing)}, "
                  f"as files of version 1.0.0 do")
    elif later:
        reason = (f"it carries the global attribute(s) {', '.join(later)}, "
                  f"written by later versions of the pipeline")
    elif int(ds.attrs["m1_spawning_offset_days"]) != M1_SPAWNING_OFFSET_DAYS:
        reason = (f"m1_spawning_offset_days is "
                  f"{int(ds.attrs['m1_spawning_offset_days'])}, "
                  f"not {M1_SPAWNING_OFFSET_DAYS}")
    else:
        return

    sys.exit(
        f"ERROR: {path} is not from version {DATASET_VERSION} of the "
        f"{DATASET_NAME}:\n"
        f"  {reason}.\n"
        f"This script builds data/aggregated.nc from version {DATASET_VERSION} "
        f"only (https://doi.org/{DATASET_DOI})."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    krico_post = os.environ.get("KRICO_POST")
    if not krico_post:
        print(
            "ERROR: KRICO_POST environment variable not set.\n"
            "Set it to the krico-post-production root directory, e.g.:\n"
            "  export KRICO_POST=/path/to/krico-post-production",
            file=sys.stderr,
        )
        sys.exit(1)

    data_dir = Path(krico_post) / "recruitment" / "data"
    if not data_dir.is_dir():
        print(f"ERROR: recruitment data dir not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Input: {DATASET_NAME}, version {DATASET_VERSION} "
          f"(https://doi.org/{DATASET_DOI}),")
    print(f"       expected in {data_dir}")

    ds = aggregate(data_dir)

    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "aggregated.nc"

    print(f"Writing {out_path}")
    encoding = {
        var: {"zlib": True, "complevel": 5}
        for var in ds.data_vars if ds[var].dtype.kind != "U"
    }
    ds.to_netcdf(out_path, encoding=encoding)

    print()
    print("Outcome totals:")
    for name, total in zip(OUTCOME_NAMES, ds["total"].values):
        print(f"  {name:28s} {int(total):14,d}")


if __name__ == "__main__":
    main()
