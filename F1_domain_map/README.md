# F1 — Domain map

Map of the study area: the computational domain, the bathymetry-defined spawning zone and continental shelf, the CCAMLR Statistical Subareas covered by the simulation, and mean sea-ice edges for two months and two periods.

Adapted from `F1_domain_map` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748`. `data/aggregated.nc`, `download_sic.sh` and `sic_provenance.txt` are unchanged copies. `aggregate.py` is the same code, reading the shapefile from `../shared/ccamlr-data/`. `plot.py` is modified (see below).

## What it shows

- **Computational domain:** 115°W to 40°E, 78°S to 40°S (dashed gray).
- **Spawning zone:** bathymetry 1000–2000 m, within the CCAMLR subareas shown (blue).
- **Continental shelf:** bathymetry < 1000 m, within the same subareas (orange).
- **CCAMLR Statistical Subareas:** 48.1, 48.2, 48.3, 48.4, 48.5, 48.6 and 88.3 (solid gray). Subarea 48.6 is split at 60°S into 48.6N and 48.6S (dotted gray), as in the spatial analyses of F4 and F5.
- **Sea-ice edges:** 15% contour of the mean monthly sea-ice concentration, for February and September, each for 1979–2015 and 2016–2025. Colour gives the period, linestyle the month. These are observations (NOAA/NSIDC G02202 Version 6, [doi:10.7265/b18j-z797](https://doi.org/10.7265/b18j-z797)), independent of the GLORYS12 sea ice that forces the simulation.
- Projection: South Polar Stereographic, central longitude 37.5°W. Land and coastlines from Natural Earth (50 m), via cartopy.

## Differences from the paper figure

- The map extends east and west of the domain's bounding box, and the three legends sit in the added width.
- The labels of 48.3 and 48.4 are on the northern boundary of their subarea rather than at its centroid, clear of South Georgia and the South Sandwich Islands.
- Larger text.

## Input data

`aggregate.py` does not read the KRICO recruitment dataset. It reads:

- `$KRICO_GLORYS12/glorys12_bathymetry.nc` — GLORYS12v1 bathymetry, from the preprocessing step of [krico-templates](https://github.com/ogourgue/krico-templates).
- `data/sic/*.nc` — NOAA/NSIDC G02202 Version 6 monthly sea-ice concentration for February and September, 1979–2025 (94 files, about 22 MB, not committed). `download_sic.sh` fetches them.
- The CCAMLR shapefile in `../shared/ccamlr-data/`.

## Files

- `download_sic.sh` — downloads the sea-ice files into `data/sic/` and rewrites `sic_provenance.txt`.
- `sic_provenance.txt` — DOI, source URL, access date and sha256 checksum of each sea-ice file behind the committed `data/aggregated.nc`.
- `aggregate.py` — masks the bathymetry to the subareas, computes the four sea-ice climatologies, writes `data/aggregated.nc`.
- `plot.py` — reads `data/aggregated.nc` and the CCAMLR shapefile in `../shared/ccamlr-data/`, writes `domain_map.png`.
- `data/aggregated.nc` — bathymetry masked to the subareas, and the four sea-ice concentration climatologies.
- `domain_map.png` — the rendered figure.

## Run

To redraw the figure from the committed `data/aggregated.nc`:

```bash
python plot.py
```

To rebuild `data/aggregated.nc` first:

```bash
export KRICO_GLORYS12=/path/to/Pre/GLORYS12
./download_sic.sh
python aggregate.py
python plot.py
```
