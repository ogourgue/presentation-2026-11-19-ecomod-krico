# Presentation: KRICO at ECOMOD, 19 November 2026

Figures and scripts for a presentation of the first paper of the KRICO project (Antarctic Krill Connectivity), given at the ECOMOD team meeting of the Royal Belgian Institute of Natural Sciences on 19 November 2026.

Author: Olivier Gourgue (RBINS)

Slides: [2026-11-19 ECOMOD KRICO](https://docs.google.com/presentation/d/1kUFjV7REQEYdEu6D1OFgO5d55Zh6K5q9bMNvMk79uLk/edit?usp=sharing) (Google Slides)

The figures and the movie are adapted for slides from [krico-paper1](https://github.com/ogourgue/krico-paper1). They show the work as presented on that day; later versions of the paper may differ. F0a and F0b are introductory diagrams drawn for the presentation; they are not in the paper.

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

Five folders differ:

* `F0a_krill_predators_fishery` is a diagram and has no data. Its `plot.py` draws it from the shapes in `pictograms.py`.
* `F0b_krill_life_cycle` is a diagram and has no data either. Its `plot.py` draws it from the shapes in `larvae.py` and in `F0a_krill_predators_fishery/pictograms.py`.
* `FS1_phenology_per_year` has no aggregation of its own. Its `plot.py` reads the aggregated data of `F2_phenology_curve`.
* The aggregated data of `FS2_currents` (about 58 MB) are not committed. Redrawing that figure needs its aggregation re-run first; see `FS2_currents/README.md`.
* `MS1_outcome_movie` is a movie. Its `plot.py` writes one frame per day and `make_movie.sh` assembles them. Its aggregated data (a few hundred MB) are not committed either; see `MS1_outcome_movie/README.md`.

## Re-running the aggregation

`aggregate.py` rebuilds `data/aggregated.nc` from the data upstream. Each folder README lists what its script reads.

F2 to F5 read the per-particle recruitment outcomes of **version 2.0.0** of the KRICO Recruitment Outcomes Dataset (1994–2025), DOI [10.5281/zenodo.22548763](https://doi.org/10.5281/zenodo.22548763). That DOI is the one of version 2.0.0 itself, not of the dataset as a whole. The dataset has other versions, and the figures here are built on 2.0.0 only; version 1.0.0, for one, gives different numbers.

The files carry no version number, so the scripts recognise the version from the global attributes of each file: version 2.0.0 files have `m1_spawning_offset_days` (24), `m1_spawning_date` and `m1_sic_source`, and neither `sic_source` nor `trajectory_sic_source`. A script stops at the first file that does not match.

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

FS1 is drawn from the aggregated data of F2, so it rests on version 2.0.0 as well.

MS1 reads the outcomes of one cohort from version 2.0.0, together with the raw trajectory of that cohort, which is not publicly archived, and the daily GLORYS12v1 sea-ice concentration; see `MS1_outcome_movie/README.md`.

F1 and FS2 do not read the recruitment dataset. The aggregation of F1 needs the GLORYS12v1 bathymetry and observed sea-ice concentration; see `F1_domain_map/README.md`. The aggregation of FS2 needs the daily GLORYS12v1 velocity fields; see `FS2_currents/README.md`.

## Folders

| Folder | Slide | Source |
|---|---|---|
| `F0a_krill_predators_fishery` | 2 | Drawn for this presentation; not in the paper |
| `F0b_krill_life_cycle` | 4 | Drawn for this presentation; not in the paper |
| `F1_domain_map` | 5 | `F1_domain_map` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F2_phenology_curve` | | `F2_phenology_curve` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F3_outcome_composition` | | `F3_outcome_composition` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F4_source_maps` | | `F4_source_maps` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `F5_destination_maps` | | `F5_destination_maps` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `FS1_phenology_per_year` | | `FS1_phenology_per_year` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `FS2_currents` | | `FS2_currents` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `MS1_outcome_movie` | | `MS1_outcome_movie` in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
| `shared/ccamlr-data` | — | CCAMLR Statistical Areas shapefile, as in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
