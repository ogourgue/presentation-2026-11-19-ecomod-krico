# F0 — Krill, its predators and the fishery

A diagram that introduces the presentation: Antarctic krill is a major food source for Southern Ocean predators and the target of the largest fishery of the region by tonnage.

This is not a figure of the paper. It was drawn for this presentation and has no counterpart in [krico-paper1](https://github.com/ogourgue/krico-paper1).

## What it shows

- Centre: Antarctic krill (*Euphausia superba*).
- Left, top to bottom: humpback whale, crabeater seal, Adélie penguin and mackerel icefish. Each stands for a group of krill predators: baleen whales, seals, penguins and other seabirds, and fish.
- Right: a krill trawler.
- An arrow runs from each of them to the krill: all five take krill.

The pictograms are stylised, not anatomical drawings. The diagram is in one colour on a transparent background, and it holds no text.

## Background

- Trathan, P. N., & Hill, S. L. (2016). The importance of krill predation in the Southern Ocean. In V. Siegel (Ed.), *Biology and Ecology of Antarctic Krill*. Springer. [10.1007/978-3-319-29279-3_9](https://doi.org/10.1007/978-3-319-29279-3_9)
- Meyer, B., et al. (2025). Adjusting the management of the Antarctic krill fishery to meet the challenges of the 21st century. *Proceedings of the National Academy of Sciences*.

## Input data

None. The diagram is drawn from the shapes defined in `pictograms.py`.

## Files

- `pictograms.py` — the six pictograms, each built as a geometry from a list of outline points.
- `plot.py` — scales and places the pictograms, draws the arrows, and writes `krill_predators_fishery.png`.
- `krill_predators_fishery.png` — the rendered diagram.

## Run

```bash
python plot.py
```

`--output` writes the diagram to another file. The scripts need `numpy`, `shapely` and `matplotlib`.
