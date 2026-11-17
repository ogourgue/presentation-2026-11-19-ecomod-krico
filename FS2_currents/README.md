# FS2 — Mean circulation

The 32-year mean circulation over the depth band in which particles are released: speed of the mean velocity vector, with streamlines of the same field.

Adapted from `FS2_currents` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` (Figure S2 of the paper). `aggregate.py` is the same code and `job.sh` is an unchanged copy. `plot.py` is modified (see below). `data/aggregated.nc` is not committed (see "Input data").

## What it shows

- **Period:** November 1993 to October 2025, 11 688 daily fields of GLORYS12v1.
- **Depth band:** 50–200 m, the band in which particles are released, averaged with layer-thickness weights.
- **Colours:** speed of the mean velocity vector (m s⁻¹), on a logarithmic scale from 0.005 to 0.5 m s⁻¹. The field spans more than a decade (median 0.03 m s⁻¹, 99th percentile 0.28 m s⁻¹), so a linear scale would show the Antarctic Circumpolar Current and nothing else.
- **Streamlines:** of the same mean field.
- Overlays: CCAMLR subarea outlines (solid gray), the split of 48.6 at 60°S (dotted gray), the computational domain (dashed gray).
- Projection: South Polar Stereographic, central longitude 37.5°W. Land and coastlines from Natural Earth (50 m), via cartopy.

How to read it:

- It is the speed of the mean vector, not the mean of the speed. It measures persistent net transport, which is what displaces a particle over 200 days. A pale region has weak net transport, not necessarily weak flow: an energetic eddy field moves little water on average.
- It is velocity, not depth-integrated transport, which would understate fast flow over the shelf.
- 50–200 m is where every trajectory starts, not where larvae stay: particles are advected in three dimensions for 200 days.
- White ocean cells are where the seabed is above 50 m, so that no model level falls in the band. White means "not represented", not "no flow".

Only the annual mean is drawn. The four seasonal means are in the aggregation as well and differ from it by a few percent in the domain-wide statistics; `--period` draws one of them.

## Differences from the paper figure

- Wider and flatter, with the colorbar to the right of the map instead of below it.
- Larger text.

## Input data

`aggregate.py` does not read the KRICO recruitment dataset. It reads the daily GLORYS12v1 velocity fields, `$KRICO_ROOT/Pre/GLORYS12/glorys12_u_YYYY_MM.nc` and `glorys12_v_YYYY_MM.nc` (384 months), from the preprocessing step of [krico-templates](https://github.com/ogourgue/krico-templates).

That is about 1.5 TB to read, and about 4.5 hours on one node: a batch job, for which `job.sh` is the SLURM script. The script saves a checkpoint every 12 months and resumes from it.

`data/aggregated.nc` is about 58 MB and is not committed, so this is the one figure of the repository that `plot.py` alone cannot redraw.

## Files

- `aggregate.py` — averages the daily velocity fields over 50–200 m and over time (annual and four seasons), writes `data/aggregated.nc`.
- `job.sh` — SLURM script that runs `aggregate.py`.
- `plot.py` — reads `data/aggregated.nc` and the CCAMLR shapefile in `../shared/ccamlr-data/`, writes `currents.png`.
- `currents.png` — the rendered figure.

## Run

Where the GLORYS12 fields are:

```bash
export KRICO_ROOT=/path/to/krico
python3 aggregate.py --limit 2      # test on the first two months
sbatch job.sh                       # all 384 months
```

Then, with `data/aggregated.nc` in place:

```bash
python plot.py
python plot.py --period DJF         # or MAM, JJA, SON
```
