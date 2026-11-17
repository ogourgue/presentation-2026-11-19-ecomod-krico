# F3 — Outcome composition

What happens to the particles as a function of release date: 32-year climatological breakdown into recruitment success and the ways of failing to recruit, as a stacked area.

Adapted from `F3_outcome_composition` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748`. `data/aggregated.nc` is an unchanged copy; `plot.py` is modified. The source folder describes how the data file is produced.

## What it shows

- All source regions together, over the 32 spawning years 1994–2025.
- X-axis: release date, 15 November to 14 March.
- Y-axis: cumulative fraction of particles (%).
- Layers, bottom to top:
  - **Domain exit** — the particle left the model domain. A limitation of the domain rather than a biological outcome, kept so that the stack sums to 100%.
  - **Ice at spawning (M1)** — compact sea ice at the spawning date, 24 days before release.
  - **Calyptopis starvation (M4)** — prolonged sea-ice cover during the calyptopis stages.
  - **Under-developed (M5a)** — furcilia IV not reached when sea ice advances.
  - **Off-shelf (M5b)** — away from shelf and slope (bathymetry ≥ 2000 m) when sea ice advances.
  - **No winter ice (M6)** — alive at the end of tracking, with no sea-ice advance detected.
  - **Recruitment success** — furcilia IV reached over shelf or slope when sea ice advances.

Particles alive at the end of tracking with sea-ice concentration still rising are counted with M6. 29 February cohorts are excluded, as in F2.

Recruitment success is green; the five M layers take a yellow-to-red gradient, lightest for the earliest criterion (M1) and darkest for the latest (M6); domain exit is gray.

## Differences from the paper figure

- Wider and flatter, with the legend to the right of the axes instead of inside them.
- Larger text.

## Files

- `plot.py` — reads `data/aggregated.nc`, writes `outcome_composition.png`.
- `data/aggregated.nc` — particle counts per spawning year, release day and outcome.
- `outcome_composition.png` — the rendered figure.

## Run

```bash
python plot.py
```
