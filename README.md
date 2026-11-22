# The Picture That Tastes of One Ingredient

[![make.fun](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![Rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/leosweet/picture-ingredient-entry/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![Reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/leosweet/picture-ingredient-entry/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

Entry for the [make.fun bounty "The picture that tastes of one ingredient"](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047).

## The picture

One ingredient, one burger: a melting-cheese cheeseburger — golden sesame
bun, wavy lettuce, tomato, a whole sheet of melted orange cheese draped
over a grilled beef patty — served on a wooden board against a warm dark
background with a soft light from above.

## How it is made

`main.py` draws the picture from scratch with the Python standard library
and Pillow only: no network, no external files, no text, no randomness.
It renders at 2x supersampling (2048x2048) and downscales with LANCZOS to
1024x1024.

Run it:

```sh
python3 main.py
```

It writes `/output/entry.png` (1024x1024 PNG, under 1 MiB). Two runs from
different working directories produce byte-identical output.
