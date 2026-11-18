# F0b — The first months of a krill, as the model sees them

A diagram that introduces the model: what happens between spawning and the first winter of Antarctic krill, which part of it the model simulates, and where sea ice and the seabed come in.

This is not a figure of the paper. It was drawn for this presentation and has no counterpart in [krico-paper1](https://github.com/ogourgue/krico-paper1).

## What it shows

Time runs from left to right, from spawning in summer to the first winter. Depth runs from the sea surface at the top to the seabed at the bottom. Neither is to scale.

- **Sea ice**, at both ends of the surface: it retreats before spawning (left) and advances again in winter (right). The open water in between is the time larvae have to develop.
- **Seabed**: the continental slope under the spawning adult, the shelf and slope under the winter sea ice. Between the two, the water is too deep for the seabed to show.
- **In grey, what comes before the simulation.** The adult spawns near the surface. The eggs sink and hatch at depth, and the nauplii swim back up. This takes 24 days. Its path is dashed.
- **In blue, what the model simulates.** Larvae drift with the currents from the first calyptopis stage, through the three calyptopis stages and the six furcilia stages, until sea ice advances. The larvae on that path and their names are dark grey.
- **Furcilia IV-VI under the winter sea ice, over the shelf and slope**: the outcome the model counts as recruitment success.

The pictograms are stylised, not anatomical drawings. The larvae are not to scale with the adult, nor with each other.

## What it stands for in the model

- **Spawning over the slope.** Particles are released where the seabed is between 1000 and 2000 m deep, the slope habitat where spawning is concentrated (Perry et al., 2019; Conroy et al., 2020).
- **24 days, not simulated.** Thorpe et al. (2019) give 23 to 26 days from spawning to the first calyptopis stage; the model applies 24. Particles are released as calyptopis I, at the position where spawning is assumed to have occurred 24 days earlier, so the transport of eggs and nauplii is neglected.
- **Sea ice at spawning.** Although spawning is not simulated, the model reads the sea-ice concentration at the release position on the spawning date: adults are assumed not to spawn under compact ice (80% or more).
- **Drift with the currents.** Larvae are passive tracers, followed for 200 days, and develop at a rate that depends on water temperature. Calyptopis starve if they stay too long under sea ice.
- **Furcilia IV.** The stage larvae must have reached when sea ice advances: earlier stages cannot feed on the algae that grow under the ice (Daly, 2004; Kohlbach et al., 2017).
- **Shelf and slope.** Where larvae must be when sea ice advances: over a seabed shallower than 2000 m.

The criteria are those of the paper (Section 2.2), adapted from Thorpe et al. (2019).

## References

- Conroy, J. A., Reiss, C. S., Gleiber, M. R., & Steinberg, D. K. (2020). Linking Antarctic krill larval supply and recruitment along the Antarctic Peninsula. *Integrative and Comparative Biology*, 60(6), 1386-1400. [10.1093/icb/icaa111](https://doi.org/10.1093/icb/icaa111)
- Daly, K. L. (2004). Overwintering growth and development of larval *Euphausia superba*: an interannual comparison under varying environmental conditions west of the Antarctic Peninsula. *Deep-Sea Research Part II*, 51(17-19), 2139-2168. [10.1016/j.dsr2.2004.07.010](https://doi.org/10.1016/j.dsr2.2004.07.010)
- Kohlbach, D., Lange, B. A., Schaafsma, F. L., David, C., Vortkamp, M., Graeve, M., van Franeker, J. A., Krumpen, T., & Flores, H. (2017). Ice algae-produced carbon is critical for overwintering of Antarctic krill *Euphausia superba*. *Frontiers in Marine Science*, 4, 310. [10.3389/fmars.2017.00310](https://doi.org/10.3389/fmars.2017.00310)
- Perry, F. A., Atkinson, A., Sailley, S. F., Tarling, G. A., Hill, S. L., Lucas, C. H., & Mayor, D. J. (2019). Habitat partitioning in Antarctic krill: Spawning hotspots and nursery areas. *PLoS ONE*, 14(7), e0219325. [10.1371/journal.pone.0219325](https://doi.org/10.1371/journal.pone.0219325)
- Thorpe, S. E., Tarling, G. A., & Murphy, E. J. (2019). Circumpolar patterns in Antarctic krill larval recruitment: an environmentally driven model. *Marine Ecology Progress Series*, 613, 77-96. [10.3354/meps12887](https://doi.org/10.3354/meps12887)

## Input data

None. The diagram is drawn from shapes: the adult krill of `pictograms.py` in `F0_krill_predators_fishery`, and the larvae of `larvae.py`.

## Files

- `larvae.py` — the pictograms of the egg, the nauplius, the calyptopis and the furcilia, built with the helpers of `F0_krill_predators_fishery/pictograms.py`.
- `plot.py` — scales and places the pictograms, draws the sea ice, the seabed, the paths and the labels, and writes `krill_life_cycle.png`.
- `krill_life_cycle.png` — the rendered diagram.

## Run

```bash
python plot.py
```

`--output` writes the diagram to another file. The scripts need `numpy`, `shapely` and `matplotlib`, and the folder `F0_krill_predators_fishery` next to this one.
