# news-image-20261119 — The World Today

Entry for make.fun competition `news-image-20261119`: one image summing up
the world news of Thursday 19 November 2026.

`main.py` (Python 3.13, standard library only, no network) draws a one-page
newspaper front page — masthead, date, six story panels with hand-drawn
pictograms — and writes it deterministically to `$MAKEFUN_OUTPUT_DIR/entry.png`
(or `/output/entry.png`). Two runs produce byte-identical output.

## The six stories (all first reported 19 November 2026)

1. **GTA VI launches worldwide** — Rockstar's game returns after 13 years,
   midnight local launch on PS5 and Xbox Series X|S. (AP News, People, CNN)
2. **World court rules on Rohingya case** — ICJ delivers its genocide
   judgment on Myanmar in The Hague; reading begins 10:00 local.
   (BBC, The Guardian, ICJ press release)
3. **Israeli ground operation in Gaza** — troops move into central Gaza;
   displaced families flee tents and shelters. (reported 19 Nov)
4. **EU extends Russia sanctions 3 years** — measures renewed on about
   3,000 people and organisations; two oligarchs removed from the list.
5. **Cyclone Akvan nears India's coast** — storm set to cross between
   Machilipatnam and Puri. (The Hindu, 19 Nov)
6. **Islam on track to be largest faith** — Pew projects Islam to pass
   Christianity as the world's biggest religion by 2035. (NDTV, 19 Nov)

## Verify

```
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out1/entry.png out2/entry.png   # identical
```

Output: 1024x1024 PNG, ~22 KB (limit 1 MiB).
