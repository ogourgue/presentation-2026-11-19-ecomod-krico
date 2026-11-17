# FS1 — Per-year phenology

Recruitment success rate as a function of release date, for each of the 32 spawning years, and the distribution of the release date at which each year peaks. Companion to F2, which shows the 32-year mean.

Adapted from `FS1_phenology_per_year` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` (Figure S1 of the paper). `plot.py` is modified (see below). As in the paper, there is no `aggregate.py`: the figure is drawn from the aggregation of F2.

## What it shows

- Upper panel: the 32 per-year curves (1994–2025), the 32-year mean, the peak of each year (open markers), the peak of the mean curve and the median of the per-year peaks (dashed lines).
- Lower panel: histogram of the 32 per-year peak dates, in 7-day bins, with their median and inter-quartile range.
- X-axis, shared by the two panels: release date, 15 November to 14 March. Release follows spawning by 24 days.
- Colours: black for the per-year curves, blue for the quantities of the mean curve, orange for the per-year quantities.

The mean curve peaks on 29 January at 7.1%. The per-year peaks have a median date of 24 January, an inter-quartile range from 15 January to 3 February, and a mean value of 7.6%. The mean curve peaks later and lower than a typical year, because averaging curves whose maxima fall on different dates broadens and flattens the result. The shaded range of F2 is the spread of success rates at a given release date; it says nothing about the spread of peak dates, which is what this figure adds.

29 February cohorts are excluded, as in F2.

## Differences from the paper figure

- Wider and flatter, with the upper panel taller than the lower one instead of two panels of equal height.
- One legend for both panels, to their right, instead of one inside each panel.
- No panel letters.
- Y-axis labels on two lines, and fewer ticks on the y-axis of the lower panel.
- Larger text.

## Input data

`plot.py` reads `../F2_phenology_curve/data/aggregated.nc`, so that the two figures are drawn from the same numbers. That file is built by `../F2_phenology_curve/aggregate.py` from version 2.0.0 of the KRICO Recruitment Outcomes Dataset (1994–2025), [10.5281/zenodo.22548763](https://doi.org/10.5281/zenodo.22548763); see `../F2_phenology_curve/README.md`.

## Files

- `plot.py` — reads the aggregation of F2, writes `phenology_per_year.png`, and prints the peak statistics quoted above.
- `phenology_per_year.png` — the rendered figure.

## Run

```bash
python plot.py
```

`--aggregated` points `plot.py` at another aggregation file.
