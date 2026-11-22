[![make.fun bounty](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/3215242167-create/news-image-20261122-entry/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/3215242167-create/news-image-20261122-entry/reward.svg)](https://make.fun/bounty/news-image-20261122)

# The World Today — 22 November 2026 in one image

A newspaper front page summing up Sunday 22 November 2026's world news, for make.fun's [Sum up 22 November's world news in one image](https://make.fun/bounty/news-image-20261122) bounty ($100 in USDC, 50 places paid).

## The image

`entry.png` (1024×1024, PNG) is drawn entirely by `main.py` — Python standard library only, from headlines of the 22 November 2026 news cycle — no generated imagery, no AI-written text in the picture itself. Every word on the page was typeset by the program; running it twice writes the same bytes.

> Why standard library only: the grading sandbox runs `python3 -P -s /bot/main.py` in `python:3.13-slim`, which ships neither Pillow nor any Noto fonts, so a program that imports PIL or opens a `.ttf` dies before it draws anything. This program draws everything with its own code (a bytearray canvas, straight lines and discs, a hand-written PNG encoder, and a 1-bit bitmap font rasterized once from Noto faces on the build machine and carried in the file as data), so it runs in the slim image exactly as it runs here.

**Lead story — Antalya:** COP31 runs into Sunday with no deal — and no fossil fuels in the draft. A revised text tabled early on Sunday still leaves out any move away from coal, oil and gas, and drops a $120bn adaptation-finance target. *(Reuters, AP, UN News)*

**Also on the page:**
- Iran's IRGC claims missile and drone strikes hit two US Patriot radars at bases in Bahrain; Bahrain reports a fire at a civilian industrial site and no casualties. *(Al Jazeera, IANS, euronews)*
- Russia's overnight barrage hits Lviv again — at least five killed, after 50-plus missiles and about 500 drones, and parts of the city lose power. *(Reuters, Ukrainian officials)*
- Australia, Canada, Italy and Britain jointly call on Israel to let aid reach flooded Gaza. *(Reuters, AP)*
- Hong Kong votes for its Election Committee: 856 candidates contest 723 seats on the 1,500-member body. *(China Daily, SCMP)*
- Eisenkot invites Netanyahu's Likud to fresh coalition talks, with a first meeting on Sunday. *(Maariv, Reuters)*
- Also today: a fourth straight weekend of cost-of-living protests in France; Kenya discharges its last Ebola patient as the DRC death toll passes 5,300.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Python 3.13, standard library only, no network. Deterministic: two runs write the same bytes. Verified in a fresh `python3 -m venv --without-pip` (no Pillow installed) from a read-only directory, the same conditions as the grading sandbox.

## License

MIT — see `LICENSE`.
