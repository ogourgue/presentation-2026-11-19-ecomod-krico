# F0 — Krill, its predators and the fishery

A diagram that introduces the presentation: Antarctic krill is a major food source for Southern Ocean predators and the target of the largest fishery of the region by tonnage, and the predators take far more of it than the fishery does.

This is not a figure of the paper. It was drawn for this presentation and has no counterpart in [krico-paper1](https://github.com/ogourgue/krico-paper1).

## What it shows

- Centre: Antarctic krill (*Euphausia superba*).
- Left: its predators, as one group. The humpback whale, the crabeater seal, the Adélie penguin, the Antarctic prion and the mackerel icefish stand for baleen whales, seals, penguins, flying seabirds and fish.
- Right: a krill trawler.
- One arrow runs from each side to the krill, with the amount of krill taken per year: 34 to 61 million tonnes (Mt) by the predators, 0.62 Mt by the fishery.
- The width of the shaft of each arrow is proportional to its amount. The predators' arrow is drawn for the middle of their range, 77 times the fishery's; over the whole range the ratio goes from 55 to 99. The arrowheads are not to scale.

The pictograms are dark grey, the arrows and their amounts blue, on a transparent background. The pictograms are stylised, not anatomical drawings.

## Numbers

- **Predators, 34 to 61 Mt per year.** Krill consumption by the main krill predators (fish, penguins, flying seabirds, seals and whales) in the Scotia Sea and Antarctic Peninsula region, from the total of Table 7 in Saunders et al. (2019). Most of the spread comes from one group, the mesopelagic lanternfish (myctophids), whose consumption is estimated between 5 and 32 Mt per year.
- **Fishery, 0.62 Mt per year.** The catch limit in force for the krill fishery in CCAMLR Subareas 48.1 to 48.4, often called the trigger level (Meyer et al., 2025). The fishery closes when it is reached, which happened for the first time in 2025. It is the sum of the largest catches recorded in each subarea before 1991, and it stands until CCAMLR agrees how to spread a larger catch over the area. The precautionary catch limit derived from the krill biomass (5.61 Mt) is nine times as large and is not in force.

The two numbers do not cover exactly the same area, and one is an estimate of consumption where the other is a limit on the catch. The diagram compares orders of magnitude.

## References

- Saunders, R. A., Hill, S. L., Tarling, G. A., & Murphy, E. J. (2019). Myctophid fish (Family Myctophidae) are central consumers in the food web of the Scotia Sea (Southern Ocean). *Frontiers in Marine Science*, 6, 530. [10.3389/fmars.2019.00530](https://doi.org/10.3389/fmars.2019.00530)
- Meyer, B., Arata, J. A., Atkinson, A., Bahlburg, D., Bernard, K., Cárdenas, C. A., Grant, S. M., Hill, S. L., Hüppe, L., Ichii, T., Kawaguchi, S., Krafft, B. A., Labrousse, S., Maschette, D., Piñones, A., Reiss, C., Siebenhüner, B., Sylvester, Z. T., & Ziegler, P. (2025). Adjusting the management of the Antarctic krill fishery to meet the challenges of the 21st century. *Proceedings of the National Academy of Sciences*, 122(37), e2412624122. [10.1073/pnas.2412624122](https://doi.org/10.1073/pnas.2412624122)

## Input data

None. The diagram is drawn from the shapes defined in `pictograms.py`, and the two amounts are set at the top of `plot.py`.

## Files

- `pictograms.py` — the seven pictograms, each built as a geometry from a list of outline points.
- `plot.py` — scales and places the pictograms, draws the arrows and their labels, and writes `krill_predators_fishery.png`.
- `krill_predators_fishery.png` — the rendered diagram.

## Run

```bash
python plot.py
```

`--output` writes the diagram to another file. The scripts need `numpy`, `shapely` and `matplotlib`.
