# Slayyyter owes the Commonwealth

A live counter of the Census fine accruing since Census night, 11 August 2026.

Slayyyter was in Australia on 11 August 2026. Almost everyone in the country on
Census night must be counted — visitors, international students and visa holders
included. She has said she didn't fill it in. The maximum penalty for failing to
complete the Census when directed to is $364 per day, so the page multiplies
$364 by the time elapsed and does not stop.

It is a joke, not a bill, and it says so on the page. Nobody is fined merely for
being late: the daily penalty applies only after the ABS serves a written Notice
of Direction, the direction is still refused, and a court convicts. The site has
no connection to the ABS or to Slayyyter.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole page — markup, styles and the ticker |
| `fine.js` | Accrual maths, shared by the page and the tests |
| `test.js` | Checks the maths. `node test.js` |

The counter runs from midnight AEST on 11 August 2026, hardcoded to UTC+10 so
every visitor sees the same figure regardless of their own timezone.

## Design

One sentence, one enormous number. Hot pink into red, with a turning Y2K
starburst, drifting blobs and twinkling sparkles — all generated in CSS, so
there are no image assets. Pirata One for the sentence (her logo has been
blackletter since the 2019 mixtape), Anton for the figure, given the chrome
treatment off the mixtape cover, Courier Prime for the footnote.

The counter scales itself down if the figure ever outgrows its line, so the
layout survives the fine reaching six and seven figures.

## Local

```sh
python3 -m http.server 8000   # then open http://localhost:8000
node test.js                  # run the maths checks
```

## Deploying

Static — no build step. Push to GitHub and set Pages to deploy from the default
branch, root folder.
