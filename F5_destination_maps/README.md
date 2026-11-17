# F5 — Destination maps by fate

Where the particles of each outcome were when their fate was determined: one map per outcome, for recruitment success and the five ways of failing to recruit (M1, M4, M5a, M5b, M6). The outcomes are described in `../F3_outcome_composition/README.md`.

Adapted from `F5_destination_maps` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748`. `data/aggregated.nc` is an unchanged copy; `plot.py` is modified. The source folder describes how the data file is produced.

## Fate position by outcome

- **Recruitment success, Under-developed (M5a), Off-shelf (M5b):** position when the winter sea-ice advance was detected.
- **Calyptopis starvation (M4):** position when the sea-ice criterion of the calyptopis stages was met.
- **Ice at spawning (M1):** position at release. The criterion is evaluated at the spawning date, 24 days earlier, but the descent-ascent cycle is not simulated, so the release position stands for the spawning position. This panel therefore shows the same distribution as the M1 panel of F4.
- **No winter ice (M6):** position on the last day of the trajectory.

## What it shows

- All 32 spawning years (1994–2025) and all release dates together.
- Per-cell quantity: the fraction of the particles of an outcome whose fate position fell in the cell. It sums to 1 within each panel.
- Grid, colours, overlays and projection as in F4 (see `../F4_source_maps/README.md`).

The colour scale is independent of the one in F4. Release positions are confined to the narrow spawning zone, while fate positions spread over the whole domain, so each figure is scaled to its own data.

Particles alive at the end of tracking with sea-ice concentration still rising are counted with M6, as in F3. Particles that left the model domain are not shown.

## Differences from the paper figure

- Two rows of three panels instead of three rows of two, in the same order.
- Panel labels without letters, in the upper-right corner of each panel.
- Fewer ticks on the colorbars.
- Larger text.

## Files

- `plot.py` — reads `data/aggregated.nc` and the CCAMLR shapefile in `../shared/ccamlr-data/`, writes `destination_maps.png`.
- `data/aggregated.nc` — particle counts per outcome on the 1° grid, by fate position.
- `destination_maps.png` — the rendered figure.

## Run

```bash
python plot.py
```
