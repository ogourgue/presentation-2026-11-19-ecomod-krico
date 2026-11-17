# F2 — Phenology curve

Recruitment success rate as a function of release date: 32-year climatological mean, with the 5th–95th percentile range across years.

Adapted from `F2_phenology_curve` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748`. `data/aggregated.nc` is an unchanged copy; `plot.py` is modified. The source folder describes how the data file is produced.

## What it shows

- All source regions together, over the 32 spawning years 1994–2025.
- X-axis: release date, 15 November to 14 March. Release follows spawning by 24 days.
- Y-axis: recruitment success rate (%), the fraction of released particles that reach the furcilia IV larval stage over shelf or slope (bathymetry < 2000 m) when sea ice advances.
- Annotations: the day of the climatological peak, and 90% of the peak value.

29 February cohorts are excluded, so that the season has the same 120 days in leap and non-leap years.

## Differences from the paper figure

- Wider and flatter.
- Larger text.

## Files

- `plot.py` — reads `data/aggregated.nc`, writes `phenology_curve.png`.
- `data/aggregated.nc` — particle counts and success rate per spawning year and release day.
- `phenology_curve.png` — the rendered figure.

## Run

```bash
python plot.py
```
