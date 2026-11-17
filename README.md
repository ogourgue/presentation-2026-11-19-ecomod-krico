# Presentation: KRICO at ECOMOD, 19 November 2026

Figures and scripts for a presentation of the first paper of the KRICO project (Antarctic Krill Connectivity), given at the ECOMOD team meeting of the Royal Belgian Institute of Natural Sciences on 19 November 2026.

Author: Olivier Gourgue (RBINS)

Slides: [2026-11-19 ECOMOD KRICO](https://docs.google.com/presentation/d/1kUFjV7REQEYdEu6D1OFgO5d55Zh6K5q9bMNvMk79uLk/edit?usp=sharing) (Google Slides)

The figures are adapted for slides from [krico-paper1](https://github.com/ogourgue/krico-paper1). They show the work as presented on that day; later versions of the paper may differ.

Related repositories:

* __[krico-paper1](https://github.com/ogourgue/krico-paper1)__ — Figures and analysis for the paper
* __[krico-post-production](https://github.com/ogourgue/krico-post-production)__ — Post-processing and recruitment classification pipeline
* __[krico-templates](https://github.com/ogourgue/krico-templates)__ — Simulation templates (Parcels + GLORYS12v1)

## Reproducing the figures

Each figure has its own folder, with `aggregate.py`, `plot.py`, the aggregated data in `data/` and the rendered figure. The aggregated data are committed, so redrawing a figure needs only:

```bash
cd <folder>
python plot.py
```

`shared/` holds files used by several figures.

## Re-running the aggregation

`aggregate.py` rebuilds `data/aggregated.nc` from the data upstream. Each folder README lists what its script reads.

F2 to F5 read the per-particle recruitment outcomes of **version 2.0.0** of the KRICO Recruitment Outcomes Dataset (1994–2025), DOI [10.5281/zenodo.22548763](https://doi.org/10.5281/zenodo.22548763). That DOI is the one of version 2.0.0 itself, not of the dataset as a whole. The dataset has other versions, and the figures here are built on 2.0.0 only; version 1.0.0, for one, gives different numbers.

To get version 2.0.0 (about 42 GB to download, 56 GB extracted) with the scripts of [krico-post-production](https://github.com/ogourgue/krico-post-production):

```bash
cd /path/to/krico-post-production/recruitment/scripts
python download_from_zenodo.py --doi 10.5281/zenodo.22548763
./extract_archives.sh
```

Give the DOI explicitly: without `--doi`, the script downloads the version that goes with its own code, which may be a later one. Then:

```bash
export KRICO_POST=/path/to/krico-post-production
cd <folder>
python aggregate.py
python plot.py
```

F1 does not read the recruitment dataset. Its aggregation needs the GLORYS12v1 bathymetry and observed sea-ice concentration; see `F1_domain_map/README.md`.

## Folders

| Folder | Slide | Source |
|---|---|---|
| `F1_domain_map` | | `F1_domain_map` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F2_phenology_curve` | | `F2_phenology_curve` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F3_outcome_composition` | | `F3_outcome_composition` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F4_source_maps` | | `F4_source_maps` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F5_destination_maps` | | `F5_destination_maps` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `shared/ccamlr-data` | — | CCAMLR Statistical Areas shapefile, as in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
