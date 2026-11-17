# F4 — Source maps by fate

Where the particles of each outcome were released: one map per outcome, for recruitment success and the five ways of failing to recruit (M1, M4, M5a, M5b, M6). The outcomes are described in `../F3_outcome_composition/README.md`.

Adapted from `F4_source_maps` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748`. `data/aggregated.nc` is an unchanged copy; `plot.py` is modified. The source folder describes how the data file is produced.

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

## Files

- `plot.py` — reads `data/aggregated.nc` and the CCAMLR shapefile in `../shared/ccamlr-data/`, writes `source_maps.png`.
- `data/aggregated.nc` — particle counts per outcome on the 1° grid, by release position.
- `source_maps.png` — the rendered figure.

## Run

```bash
python plot.py
```
