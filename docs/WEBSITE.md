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

1. Edit `site/data/leaderboard.json`. Each model has two XQA scores, 24 LQA
   scores in the declared language order, and the reported AVG. Keep model names
   exactly as supplied. Record the result source, Judge and model-card link.
2. Update `site/data/leaderboard.csv` to match the same values and order.
3. Update the displayed date and filter counts in `site/index.html` if needed.
4. Run the validator and check sorting, filters, model search, empty results,
   CSV download, model details and example language switches in the browser.
5. Push the reviewed changes to `main`. The Pages workflow deploys the site.

AVG weights all 70 configurations equally. The two XQA summary columns each
represent 23 configurations; each LQA language represents one. Do not average
just the displayed 26 component columns. Preserve submitted rounded values;
validate aggregates with the unrounded per-configuration results when available.
The overview LQA mean is explicitly derived from the 24 rounded display values.

## Published snapshot and provenance

The initial website snapshot contains nine model rows supplied by the maintainer
on 2026-09-28. Scores are transcribed, not newly evaluated by the website.
The maintainer confirmed exact matching followed by text-only GPT-6 Astra
judging for non-matches for all nine rows. Additional API runs have not supplied
raw predictions or failure counts; the public page states this limitation.
Existing local runs retain their disclosed errors. GPT-5.5 is omitted because
its evaluation is incomplete. Publishing the website never resumes API jobs.

Use **open weights**, rather than an unconditional open-source label, because
licenses differ. Official weight repositories checked on 2026-09-28:

- [Kimi-K3](https://huggingface.co/moonshotai/Kimi-K3)
- [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)
- [MiniMax-M3](https://huggingface.co/MiniMaxAI/MiniMax-M3)
- [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)
- [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash)

The remaining GPT and Gemini entries are categorized as closed models.
All supplied runs use APIs; open-weight availability does not imply local serving.

`site/data/examples.json` contains two selected public release cases, each with
all 24 visual languages and the corresponding LQA/XQA questions. The gallery
displays all 24 images for the selected chart or table, with matching question
and answer controls and links to full-resolution originals.
Images are byte-identical copies from the published current release. SHA-256,
case IDs, QA IDs and source attribution are included. Source-specific dataset
terms still apply. These examples are for illustration, not quality certification.
The hero shows the same released ChartQA case in English, Chinese, Japanese
and Arabic, using the original localized PNGs. Its question excerpts omit only
the answer-language instruction; source and case ID are displayed.

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
interactive code in this repository are original; no template code or third-party
logos were copied. No publication venue, accepted-paper status, author list or
paper link is invented.

## Institutional identity

MBZUAI is displayed as an institutional logo without an affiliation rank. The logo row wraps to accommodate additional institutions.
The site uses the official English navy logo, without modification, from the
University's downloadable brand assets. Navy, sand and white follow the March
2026 brand palette. See [asset provenance and attribution](../site/assets/MBZUAI-ASSET-NOTICE.md).
The project icon remains separate from the University logo. No authors, research
lab, department, publication acceptance or institutional endorsement is inferred.
