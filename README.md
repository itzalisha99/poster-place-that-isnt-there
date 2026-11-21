# KORVATH — The City That Sails on a Whale

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/itzalisha99/poster-place-that-isnt-there/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/itzalisha99/poster-place-that-isnt-there/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for a place that isn't there: **KORVATH, the city that
sails on a whale**. A giant whale carries a whole lit city on its back
across a dusk sea — red-and-white lighthouse, glowing windows, a small
sailboat below to show the scale. Drawn from scratch with PIL
(`draw_poster.py`), no AI image generation, no copied art.

## Run

```sh
python3 main.py
```

Writes the poster to `$MAKEFUN_OUTPUT_DIR/entry.png` (default
`/output/entry.png`), a 1024x1024 PNG under 1 MiB, and checks the PNG
signature, size and dimensions before it exits.

## Files

- `main.py` — entrypoint (stdlib only): copies `entry.png` to the
  output dir and validates it.
- `draw_poster.py` — the program that draws the poster.
- `entry.png` — the poster itself, 1024x1024.

Built for the make.fun bounty "The Poster for a Place That Isn't
There". Referral code: `y05d5qm6`.
