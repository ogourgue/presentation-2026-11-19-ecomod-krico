# F4 — Source maps by fate

Where the particles of each outcome were released: one map per outcome, for recruitment success and the five ways of failing to recruit (M1, M4, M5a, M5b, M6). The outcomes are described in `../F3_outcome_composition/README.md`.

Adapted from `F4_source_maps` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748`. `data/aggregated.nc` is an unchanged copy. `aggregate.py` is the same code, with the input dataset and its version stated. `plot.py` is modified (see below).

## What it shows

- All 32 spawning years (1994–2025) and all release dates together.
- Per-cell quantity: the fraction of the particles of an outcome that were released in the cell. It sums to 1 within each panel.
- Grid: 1° × 1° in longitude and latitude.
- Colours: green for recruitment success, red for the five other panels, on one scale shared by all six panels. The scale ends at the 99th percentile of the nonzero cells of all panels pooled.
- Overlays: CCAMLR subarea outlines (solid gray), the split of 48.6 at 60°S (dotted gray), the computational domain (dashed gray).
- Projection: South Polar Stereographic, central longitude 37.5°W. Land and coastlines from Natural Earth (50 m), via cartopy.

Particles alive at the end of tracking with sea-ice concentration still rising are counted with M6, as in F3. Particles that left the model domain (0.8% of all particles) are not shown.

## Differences from the paper figure

- Two rows of three panels instead of three rows of two, in the same order.
- Panel labels without letters, in the upper-right corner of each panel.
- Larger text.

## Input data

`aggregate.py` reads the per-particle recruitment outcomes of version 2.0.0 of the KRICO Recruitment Outcomes Dataset (1994–2025), [10.5281/zenodo.22548763](https://doi.org/10.5281/zenodo.22548763), from `$KRICO_POST/recruitment/data/`. The DOI is that of version 2.0.0 itself. The script checks every file it reads and stops if one comes from another version. The main README explains how to get version 2.0.0.

## Files

- `aggregate.py` — bins the release positions of the particles of each outcome on the 1° grid, writes `data/aggregated.nc`.
- `plot.py` — reads `data/aggregated.nc` and the CCAMLR shapefile in `../shared/ccamlr-data/`, writes `source_maps.png`.
- `data/aggregated.nc` — particle counts per outcome on the 1° grid, by release position.
- `source_maps.png` — the rendered figure.

## Run

To redraw the figure from the committed `data/aggregated.nc`:

```bash
python plot.py
```

To rebuild `data/aggregated.nc` first:

```bash
export KRICO_POST=/path/to/krico-post-production
python aggregate.py
python plot.py
```
