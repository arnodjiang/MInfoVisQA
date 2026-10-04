# Multilingual Visual Benchmark Harness + Skill

Translation uses the Google Translate API (Google Cloud Translation Basic v2, NMT). The LLM translation adapter is an optional alternative enabled only with `TRANSLATION_BACKEND=llm`. Visual reconstruction, quality review and answer judging are separate from translation.

Reconstruct a chart as Python, or extract structured table cells; translate visible labels through a replaceable translator; render multilingual images while preserving numerical data, source identity and executable original/translated code.

This directory is a self-contained code distribution and a Codex skill. The skill guides chart recovery; the harness runs prepared specifications. It does **not** claim automatic recovery of arbitrary charts or automatic benchmark acceptance.

## Quick start

```sh
python -m pip install -r requirements.txt
python scripts/visual_harness.py run --spec examples/chart.json --output /tmp/mvisqa-chart --languages en,zh --translations examples/chart_locales.json --font /path/to/Unicode.ttf
python scripts/visual_harness.py run --spec examples/table.json --output /tmp/mvisqa-table --languages en,zh,ar --translations examples/table_locales.json --font /path/to/Unicode.ttf
```

These synthetic examples make no API calls. The printed output directory contains HTML, PNGs, dictionaries, manifests and standalone Python code for each language. On macOS the default Arial Unicode font may be available; on other systems explicitly supply a covering font. Fonts are not redistributed.

For live translation, omit `--translations`, set `GOOGLE_TRANSLATE_API_KEY` and `GOOGLE_TRANSLATE_ENDPOINT` for Cloud Translation Basic v2, or pass an explicit `--env-file`. The default is `TRANSLATION_BACKEND=google`. Set `TRANSLATION_BACKEND=llm` and `OPENAI_*` only for optional LLM translation. Responses are cached by provider and source content; incomplete or structurally invalid translations stop the run. Use the harness within this repository so the shared translation adapter is available.

```sh
python scripts/visual_harness.py prepare-table --input input.html --output /tmp/table.json
python scripts/visual_harness.py run --spec /tmp/table.json --output /tmp/mvisqa-output --env-file /path/to/.env --font /path/to/Unicode.ttf
python -m unittest discover -s tests -v
```

## Skill installation

Copy this directory to `~/.codex/skills/multilingual-visual-benchmark`, retaining scripts, examples and references. Invoke `$multilingual-visual-benchmark`. The project copy is the version-controlled source; refresh the installed copy when updating it. Skill discovery may require opening a new task/session.

## Documentation

- [SKILL.md](SKILL.md): agent workflow and admission checks.
- [Input and renderer contract](references/contract.md): chart adapters, cell grid, translator API and artifacts.
- [Method and evaluation](references/method.md): harness/skill/agent roles, candidate contributions, ablations and limitations.

MIT applies to code in this directory only. The examples are synthetic. Upstream datasets, original figures, model outputs and system fonts retain their own terms; no dataset or credentials are bundled. No external repository has been published by this operation.
