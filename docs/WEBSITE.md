# Benchmark website

Public homepage: https://arnodjiang.github.io/MInfoVisQA/

The dependency-free static website lives in `site/`. GitHub Actions publishes
only that directory through GitHub Pages on changes to the website, its validator
or the Pages workflow. No API keys, model calls, local evaluation runs or full
dataset exports are part of the website build.

## Preview and validate

```bash
python scripts/site/validate.py
python -m http.server 8780 --bind 127.0.0.1 --directory site
```

Open http://127.0.0.1:8780/. Serve over HTTP; JSON loading is not intended for
`file://` navigation. There is no package installation or frontend build step.

## Update results

1. Replace `site/data/paper-main-table.tex` with the current manuscript main table.
2. Run `python scripts/site/sync_paper_table.py` to regenerate JSON and CSV without changing published scores; update the snapshot date in that script when making a new release.
3. The page derives its date, model counts and CSV filename from the JSON. Bump the JavaScript/data version query when publishing a new snapshot.
4. Run `python scripts/site/validate.py` and check sorting, filters, model search, empty results, model details and example language switches.
5. Push reviewed changes to `main`; the Pages workflow deploys `site/`.

AVG weights all 70 configurations equally. The two XQA summary columns each
represent 23 configurations; each LQA language represents one. Do not average
just the displayed 26 component columns. Preserve submitted rounded values;
validate aggregates with the unrounded per-configuration results when available.
The overview LQA mean is explicitly derived from the 24 rounded display values.

## Published snapshot and provenance

The current snapshot follows the manuscript main table: 25 models, including GPT-5.5, with 675 score cells. It supersedes the nine-model September snapshot. Scores are transcribed, not newly evaluated by the website. The current scoring protocol uses exact matching followed by text-only GPT-6 Astra adjudication for non-matches.

Model groups follow the paper: 5 proprietary, 16 general-purpose open-weight, and 4 chart-specialized models. Existing model-card links are retained where documented; links for additional models are not inferred from their names. Serving through an API does not determine weight availability. Row-specific failure counts from older snapshots must not be silently transferred to new results.

`site/data/examples.json` contains two selected public release cases, each with
all 24 visual languages and the corresponding LQA/XQA questions. The gallery
displays all 24 images for the selected chart or table, with matching question
and answer controls and links to full-resolution originals.
Images are byte-identical copies from the published current release. SHA-256,
case IDs, QA IDs and source attribution are included. Source-specific dataset
terms still apply. These examples are for illustration, not quality certification.
The hero contains a 46-second research demo with original benchmark visuals, a recorded English/Japanese prediction pair and paper-derived LQA profiles. Playback is user-controlled. The README uses a linked animated preview. Sources and a transcript accompany the video.

## Deployment

In repository Settings → Pages, select **GitHub Actions** as the build source.
The `Deploy benchmark website` workflow uses the official Pages actions and
minimal `contents: read`, `pages: write`, `id-token: write` permissions.
The build uploads `site/` only. Inspect the workflow and `github-pages`
environment for deployment status. It uses the repository path `/MInfoVisQA/`;
asset links are relative so local previews also work.

## Design references

The information hierarchy was informed by the
[MMMU project and leaderboard](https://mmmu-benchmark.github.io/) and
[CharXiv project page](https://charxiv.github.io/): introduction, benchmark
examples, results and evaluation protocol. The layout, styles, diagram and
interactive code in this repository are original; no third-party template code was copied. Official institution logos are used with source attribution. No publication venue, accepted-paper status, author list or
paper link is invented.

## Institutional identity

The four author affiliations appear in manuscript order: MBZUAI, Georgia Tech, the University of Tokyo and UIUC. The responsive logo row preserves this order.
The site uses the official English navy logo, without modification, from the
University's downloadable brand assets. Navy, sand and white follow the March
2026 brand palette. See [asset provenance and attribution](../site/assets/MBZUAI-ASSET-NOTICE.md).
The project icon remains separate from the University logo. No authors, research
lab, department, publication acceptance or institutional endorsement is inferred.

### Manuscript synchronization (13 October 2026)

The public leaderboard now mirrors the 25-model main table. `site/data/paper-main-table.tex` is a frozen copy of the paper's current single-table source. Run `python scripts/site/sync_paper_table.py`, then `python scripts/site/validate.py` when updating this snapshot. Validation checks all 675 score cells and model groups against that source and records its SHA-256. Preserve the manuscript AVG; LQA mean is a separate display-only calculation. Model-card links are optional and must not be guessed.

The header and README use official MBZUAI, Georgia Tech, University of Tokyo and UIUC logos in manuscript order. Georgia Tech: https://www.gatech.edu/themes/custom/gatech/images/gatech-color_logo.png ; Tokyo: https://www.u-tokyo.ac.jp/content/400235960.png (only blank margins cropped, original retained); UIUC: https://cdn.brand.illinois.edu/wordmarks/formal/orange-and-blue.svg . MBZUAI's existing official SVG is retained.
