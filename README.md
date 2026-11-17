# Presentation: KRICO at ECOMOD, 19 November 2026

Figures and scripts for a presentation of KRICO Paper 1 at the bi-weekly ECOMOD team meeting (RBINS, 19 November 2026).

Author: Olivier Gourgue (RBINS)

Slides: (link to be added)

Related repositories:

* __[krico-paper1](https://github.com/ogourgue/krico-paper1)__ — Figures and analysis for the paper; the source of most figures here
* __[krico-post-production](https://github.com/ogourgue/krico-post-production)__ — Post-processing and recruitment classification pipeline
* __[krico-templates](https://github.com/ogourgue/krico-templates)__ — Simulation templates (Parcels + GLORYS12v1)

## Format

This repository follows a fixed format, one repository per presentation, named `presentation-<date>-<context>-<project>`. Every presentation has one context; it can cover no project, one or several, so projects come last.

- **One folder per figure.** Each holds `plot.py`, the data it reads in `data/`, the rendered figure, and a `README.md`. Running `python plot.py` inside the folder reproduces the figure.
- **`shared/` holds what is identical across figures**: the CCAMLR shapefile and anything else several folders read. Nothing else is shared between folders.
- **Rendered figures are always committed**, so the slides never depend on data that is not here.
- **Data files under about 5 MB are committed.** Larger files are gitignored; the folder's `README.md` then says where the data lives and how to regenerate it.
- **A figure taken from another repository is a copy, not a link.** The folder's `README.md` records the source repository and commit. This repository is a snapshot of what was shown on the day; later changes to the paper do not propagate here.

## Folders

| Folder | Slide | Source |
|---|---|---|
| `shared/ccamlr-data` | — | [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |

## Environment

- `environment-local.txt` — package versions on the laptop (MacPorts Python), written with `python -m pip list --format=freeze`.
- `environment-hpc.txt` — modules loaded on the HPC (`module list`). Present only if a folder runs there.

These files record what produced the figures; they are not installers.
