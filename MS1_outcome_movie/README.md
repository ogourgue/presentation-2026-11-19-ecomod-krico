# MS1 — Outcome movie

One release-day cohort followed from release to the end of tracking, with particles turning green or red on the day their outcome is decided. It shows in motion what F3 to F5 show in aggregate: the drift during summer, the sea-ice advance from April, and where larvae end up ready or not ready to overwinter.

Adapted from `MS1_outcome_movie` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` (Movie S1 of the paper). `aggregate.py` is the same code, with the input dataset and its version stated. `job.sh` is an unchanged copy, and `make_movie.sh` differs in its comments only. `plot.py` is modified (see below). `data/aggregated.nc` is not committed (see "Input data").

## What it shows

- **Cohort:** a single release day, chosen from F2's aggregation (see below). By default 29 January 2006, spawned on 5 January 2006, all ~546,000 particles.
- **Date:** above the map, the day shown.
- **Particles:** only particles that drift are shown.
  - translucent gray while drifting, at their daily position;
  - green at their fate position from the day recruitment success is decided, and they stay;
  - red at their fate position from the day M4, M5a or M5b is decided, fading out over `FADE_DAYS` (5) days so the map stays readable;
  - M1 particles are not shown: they are never spawned;
  - M6 particles (with censored folded in, as in the paper) stay gray to the end;
  - domain exits drift in gray until deleted, then disappear. They are a modelling limitation, not an outcome.
- **Sea ice:** daily GLORYS12 concentration above the 15% advance threshold, block-averaged to 1/4°, as a single colour. These are the fields the simulation and the classification use, not the observed climatologies of F1.
- **Shelf-slope zone:** bathymetry shallower than 2000 m, the bathymetric condition for recruitment success (its complement is M5b), as a translucent light gray drawn over the sea ice. It comes from F1's bathymetry, which is masked to the CCAMLR subareas, so the zone is drawn inside them only. The strip south of the GLORYS12 grid (about 77°S) is filled with the same colour across the domain's longitudes, since it is shelf in front of the Weddell ice shelves.
- **Base map:** F1's land, coastline, CCAMLR outlines and domain boundary, imported from `../F1_domain_map/plot.py`. F1's subarea labels, 48.6 split, bathymetry zones, sea-ice climatologies and legends are left out.
- **Format:** 1748 × 1496 px frames, one per tracking day, from release (frame 0) to the end of tracking (frame 200), played at 10 frames per second (about 20 s).

Outcome timing comes from the archived fate day (`travel_time`) of the recruitment classification, so the movie cannot disagree with it:

- M4 is decided when the starvation threshold is crossed, during the calyptopis stages.
- Success, M5a and M5b are decided at each particle's own sea-ice advance, from 1 April onward, so they appear as the ice edge moves north.
- M6 is only decided at the end of tracking, which is where the movie ends: those particles are still gray on the last frame, and that gray cloud is the larvae winter sea ice never reached.
- M1 is decided at spawning, before release, so those particles never enter the movie.

## Cohort choice

`aggregate.py` picks the cohort from `../F2_phenology_curve/data/aggregated.nc` instead of a hand-picked date:

1. the climatological peak release date, the maximum of the 32-year mean curve (29 January, as in F2);
2. among spawning years up to 2016, the year whose own peak release date is closest to it;
3. ties broken by the peak value closest to the median of per-year peaks.

The cohort is that year's own peak release date. Years after 2016 are excluded so the movie cannot be read as a statement about the post-2016 low-ice regime. This gives spawning year 2006, whose own peak falls exactly on 29 January. `--date` overrides the choice.

## Differences from the paper movie

- The frame holds the date, the map and the legend only: no title, no subtitle, no explanatory text.
- Wider than high instead of square, with the map across the full width of the frame.
- Larger text, and the legend in two columns instead of three.
- The per-year series of the paper repository (`job_series.sh`) is not included.

## Input data

`aggregate.py` reads, for the one cohort:

- `$KRICO_RUNS/KRICO_*/YYYY_MM_DD.nc` — its raw trajectory (not publicly archived; see [krico-post-production](https://github.com/ogourgue/krico-post-production)).
- `$KRICO_POST/recruitment/data/YYYY_MM_DD.nc` — its recruitment outcomes, from version 2.0.0 of the KRICO Recruitment Outcomes Dataset (1994–2025), [10.5281/zenodo.22548763](https://doi.org/10.5281/zenodo.22548763). The DOI is that of version 2.0.0 itself. The script checks the file and stops if it comes from another version. The main README explains how to get version 2.0.0.
- `$KRICO_GLORYS12/glorys12_ice_YYYY_MM.nc` — daily GLORYS12v1 sea-ice concentration for the months covered by tracking, from the preprocessing step of [krico-templates](https://github.com/ogourgue/krico-templates).
- `../F2_phenology_curve/data/aggregated.nc` — for the cohort choice (committed).

The trajectory and recruitment files are matched row by row. `aggregate.py` checks this by comparing each particle's trajectory position on its fate day with the archived fate position, and stops if they disagree.

`data/aggregated.nc` is a few hundred MB and is not committed, and neither are the frames. So `plot.py` alone cannot redraw the movie: the aggregation has to be re-run first, where the raw trajectories are.

`plot.py` also reads `../F1_domain_map/data/aggregated.nc` (committed) for the shelf-slope zone, and the CCAMLR shapefile in `../shared/ccamlr-data/`.

## Files

- `aggregate.py` — reads the cohort's raw trajectory, its recruitment file and the daily sea ice, and writes `data/aggregated.nc`: daily positions up to each particle's fate day, outcome, fate day and fate position per particle, and the coarsened daily sea ice.
- `job.sh` — SLURM script that runs `aggregate.py`.
- `plot.py` — reads `data/aggregated.nc` and writes `frames/frame_NNN.png`.
- `make_movie.sh` — assembles the frames into `outcome_movie.mp4` with ffmpeg.
- `outcome_movie.mp4` — the rendered movie.

## Run

Where the raw trajectories are:

```bash
export KRICO_RUNS=/path/to/runs
export KRICO_POST=/path/to/krico-post-production
export KRICO_GLORYS12=/path/to/Pre/GLORYS12
sbatch job.sh                          # or: sbatch job.sh --date 2006-01-29
```

Then, with `data/aggregated.nc` in place:

```bash
python plot.py --frames 120:121 --stride 10    # quick look at one frame
python plot.py                                 # all frames, a few seconds each
./make_movie.sh                                # FPS=10 by default
```

Frame ranges are independent (`--frames 0:100`, `--frames 100:`), so a long render can be split across processes.
