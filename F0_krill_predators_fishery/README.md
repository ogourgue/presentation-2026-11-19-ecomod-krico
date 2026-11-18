# F0 — Krill, its predators and the fishery

A diagram that introduces the presentation: Antarctic krill is a major food source for Southern Ocean predators and the target of the largest fishery of the region by tonnage, and the predators take far more of it than the fishery does.

This is not a figure of the paper. It was drawn for this presentation and has no counterpart in [krico-paper1](https://github.com/ogourgue/krico-paper1).

## What it shows

- Centre: Antarctic krill (*Euphausia superba*).
- Left: its predators, as one group. The humpback whale, the crabeater seal, the Adélie penguin and the mackerel icefish stand for baleen whales, seals, penguins and other seabirds, and fish.
- Right: a krill trawler.
- One arrow runs from each side to the krill, with the amount of krill taken per year: at least 55 million tonnes (Mt) by the predators, 0.62 Mt by the fishery.
- The width of the shaft of each arrow is proportional to its amount, a ratio of 89 to 1. The arrowheads are not to scale.

The pictograms are dark grey, the arrows and their amounts blue, on a transparent background. The pictograms are stylised, not anatomical drawings.

## Numbers

- **Predators, at least 55 Mt per year.** Krill consumption by the main vertebrate groups in CCAMLR Subareas 48.1 to 48.3 (Antarctic Peninsula and Scotia Sea), from Table 1 of Trathan & Hill (2016): fish 37, seals 8, seabirds 8 and whales 2. The authors give it as a minimum, and the estimates for fish are the least certain.
- **Fishery, 0.62 Mt per year.** The catch level at which CCAMLR closes the krill fishery in Subareas 48.1 to 48.4 (Conservation Measure 51-01). The fishery reached it in 2025 and in 2026.

The two numbers do not cover exactly the same area, and one is an estimate of consumption where the other is a catch limit. The diagram compares orders of magnitude.

## References

- Trathan, P. N., & Hill, S. L. (2016). The importance of krill predation in the Southern Ocean. In V. Siegel (Ed.), *Biology and Ecology of Antarctic Krill*. Springer. [10.1007/978-3-319-29279-3_9](https://doi.org/10.1007/978-3-319-29279-3_9)
- Meyer, B., et al. (2025). Adjusting the management of the Antarctic krill fishery to meet the challenges of the 21st century. *Proceedings of the National Academy of Sciences*.
- CCAMLR. Conservation Measure 51-01, Precautionary catch limitations on *Euphausia superba* in Statistical Subareas 48.1, 48.2, 48.3 and 48.4.

## Input data

None. The diagram is drawn from the shapes defined in `pictograms.py`, and the two amounts are set at the top of `plot.py`.

## Files

- `pictograms.py` — the six pictograms, each built as a geometry from a list of outline points.
- `plot.py` — scales and places the pictograms, draws the arrows and their labels, and writes `krill_predators_fishery.png`.
- `krill_predators_fishery.png` — the rendered diagram.

## Run

```bash
python plot.py
```

`--output` writes the diagram to another file. The scripts need `numpy`, `shapely` and `matplotlib`.
