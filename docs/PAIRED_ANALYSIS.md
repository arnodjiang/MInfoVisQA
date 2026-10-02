# Paired visual-language diagnostics

This analysis reuses **frozen main-table predictions and text-only judgments**.
Following the user's 2026-10-02 instruction, it does not rerun failed requests,
repair judgments, remove configurations, or replace leaderboard scores.
No model API is called by either analysis command.

```sh
.venv/bin/python -m scripts.evaluation.paired_analysis
.venv/bin/python -m scripts.evaluation.paired_report
.venv/bin/python -m unittest tests.test_paired_analysis
```

The default four run directories are declared in `configs/paired_runs.json`. Other
leaderboard models need per-configuration predictions and judgments; aggregate
accuracy alone cannot recover correctness flips.

## Inputs and validation

- 128 seed identities, each with 24 LQA and 46 EN/ZH XQA configurations.
- All 8,960 reference and judgment IDs are checked per model; joins use IDs.
- Frozen reference bytes, current image bytes, question/answer/context fields,
  request image hashes and nominal prompts are checked.
- Every judgment fingerprint is recomputed from its frozen reference,
  prediction, effective corrected reference and Judge prompt.
- Within each fixed EN/ZH question, all 24 variants share question, answer,
  effective reference, optional context and nominal prompt.
- Recorded selected-attempt prompts are checked when hashes exist. Some legacy
  attempts lack those hashes. Format-only plain-answer fallback and generation
  setting changes are recorded, not removed. This is an analysis of the historical
  evaluation protocol, not evidence of perfectly uniform execution settings.
- Recomputed baseline/XQA averages must equal the stored semantic leaderboard.

## Metrics

For each seed, compare each of the other 23 visual languages against the
same-language visual with fixed English or Chinese question and answer.
Delta is cross-visual accuracy minus baseline accuracy (percentage points).
C→W and W→C use all 128 × 23 pairs, not just initially correct/incorrect cases.
Subgroup flip rates use 23 × subgroup seed count.

The coverage curve reports the fraction of seeds correct in at least k visual
languages, k=1,…,24. All-wrong seeds do not count as stable successes.

Intervals use 10,000 percentile bootstrap draws, random seed 20261002, resampling
whole seed clusters. The seed's 24 variants remain together. These intervals
measure empirical seed-sampling uncertainty, not repeated API variance or
representativeness of all charts/tables. They are marginal, not simultaneous
confidence bands. A one-seed subgroup is descriptive only.

## Deliverables

`outputs/paired_analysis/`:

- `paired_metrics.json`: point estimates and full 95% intervals.
- `input_validation.json`: provenance checks and protocol limitations.
- `paired_records.jsonl`: 24,576 records (4 models × 128 seeds × 2 query languages × 24 visuals).
- `subgroup_metrics.csv`: chart/table, table structure and answer-translation groups.
- `coverage_curves.csv`: points and marginal intervals.
- `cross_language_coverage.pdf`: two-panel vector figure for Overleaf `img/`.

Paper fragments:

- `paper/tables/paired_results.tex`: main paired-sensitivity table.
- `paper/tables/paired_subgroups.tex`: appendix subgroup tables.
- `paper/paired_analysis_results.tex`: methods, results paragraph and figure insertion.
- `paper/paired_results_preview.tex`: self-contained table preview.

For the existing answer-type classification, numeric/symbol/fixed identifiers
are translation-invariant; references with translatable lexical content belong
to the other group. This reuses `configs/answer_translation_audit.csv`;
it does not claim a new independent human audit of borderline cases.

## Original-image control: cancelled, not launched

Source preflight verified 119 available original rasters and 9 text-only source
tables. The frozen benchmark is not changed. The source manifest retains those
bindings, but original/reconstruction semantic eligibility is not established
for the full pool and no aggregate control result is reported.

Before the user's stop instruction, two single-case API smoke tests completed
(one GPT-6 Astra, one Gemini). They both returned 12.7 for the source table case
`2bf86a8ac478956722f8`. Their logs are isolated in `outputs/paired_analysis/api_probe/`;
they are **not leaderboard predictions or experimental accuracy estimates**.
No batch original-image inference job was launched. No inference runner or
scheduled continuation for that cancelled experiment is installed.

## Interpretation

Gemini's Chinese net delta is -0.034 pp despite 2.921% C→W and 2.887% W→C.
GPT-5.6-Luna's Chinese net delta is -0.543 pp despite 6.386% C→W and 5.842% W→C.
Thus a near-zero average difference need not mean instance-level stability.
This does not isolate OCR, translation quality, fonts, layout, or API stochasticity.
Subgroup score differences are descriptive, not causal construction ablations.

## Add models on another machine

Edit `configs/paired_runs.json` or supply `--runs /path/to/runs.json`:

```json
[
  {"name": "Model display name", "run": "data/evaluation/model_run"}
]
```

Relative run paths resolve from the repository root; absolute paths are accepted.
Every run needs `manifest.json`, `references.jsonl`, `prompt.txt`, per-ID
`requests/` and `predictions/`, and `llm_judge_text_v2/` containing the frozen
Judge manifest, prompt, corrections, judgments and scores. Other formats need
an explicit adapter preserving identities and scoring; do not fabricate hashes.
The plot includes every configured model and expands the legend for additional
models. No API calls occur.

```sh
.venv/bin/python -m scripts.evaluation.paired_analysis \
  --runs configs/paired_runs.json \
  --dataset /path/to/validation_release/val.candidates.jsonl \
  --output outputs/paired_analysis
.venv/bin/python -m scripts.evaluation.paired_report --output outputs/paired_analysis
```

The default answer-category audit is published at
`configs/answer_translation_audit.csv`; override with `--answer-audit` if needed.
The report does not require original-image archives by default. Its optional
`--source-preflight` is a local provenance check for the original four-model
setup, not an inference command. The drafted prose currently discusses the four
original models; revise it from the new metrics when adding models.

A copy of the current vector figure is published at
`paper/img/cross_language_coverage.pdf`. Raw predictions and API logs remain local.
