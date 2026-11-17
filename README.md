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

Each figure has its own folder, with a `plot.py`, the data it reads in `data/`, and the rendered figure. To reproduce one:

```bash
cd <folder>
python plot.py
```

`shared/` holds files used by several figures.

## Folders

| Folder | Slide | Source |
|---|---|---|
| `shared/ccamlr-data` | — | CCAMLR Statistical Areas shapefile, as in [krico-paper1](https://github.com/ogourgue/krico-paper1) @ `e8ae748` |
