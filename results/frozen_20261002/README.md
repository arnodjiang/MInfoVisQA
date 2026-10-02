# Frozen local results for cross-machine aggregation

Five locally evaluated models are included: **GPT-6 Astra, Gemini-3.8-Flash,
GPT-5.6-Sol, GPT-5.6-Luna and GPT-5.5**. Each has 8,960 frozen semantic decisions
on the same 128 seeds and 70 language configurations. Total: **44,800 decisions**.
No model was rerun or rejudged for this export. Original failure decisions remain.

## Use on another machine

```sh
git pull origin main
```

Start with `paired_seed_correctness.csv`. It has 1,280 rows:
5 models × 128 seeds × 2 fixed question languages. Each row contains:

- `model`, `case_id`, `query_language`, `visual_family`, `visual_kind`;
- 24 language-code columns holding binary correctness, **not accuracy percentages**.

For EN questions use the `en` column as the baseline; for ZH use `zh`.
The other 23 columns form the cross-visual conditions. Thus this file alone
supports the second table, both flip directions, coverage curves and seed-cluster
bootstrap. Preserve row identities when combining with another model.

```python
import csv
import numpy as np
from scripts.evaluation.paired_analysis import seed_metrics, estimate, plot
from scripts.evaluation.score import LANGUAGES

with open('results/frozen_20261002/paired_seed_correctness.csv') as f:
    records = list(csv.DictReader(f))
rows = sorted(
    (r for r in records if r['model'] == 'GPT-5.5' and r['query_language'] == 'en'),
    key=lambda r: r['case_id'],
)
y = np.array([[int(r[lang]) for lang in LANGUAGES] for r in rows])
metrics = estimate(seed_metrics(y, LANGUAGES.index('en')), reps=10000, seed=20261002)
# Columns: baseline ACC, cross-visual ACC, delta pp, C->W %, W->C %.
coverage = [100 * (y.sum(axis=1) >= k).mean() for k in range(1, 25)]
```

For chart/table results select rows by `visual_family` before calculating metrics.
For the overall flip rates keep all 128 rows (denominator 128 × 23).
For bootstrap keep each seed's entire vector of 24 decisions together.

## Full configuration results

- `frozen_correctness.csv.gz`: all 44,800 configuration-level decisions, with
  model, configuration `id`, binary `correct`, inference status, Judge method
  and final verdict.
- `configuration_bindings.csv.gz`: 8,960 unique configurations; join on `id` for
  seed identity, languages, visual family/type and an input-binding hash.
- `paired_metrics.json`: numerical paired metrics and 10,000-draw bootstrap CIs.
- `coverage_curves.csv`, `subgroup_metrics.csv`, `paired_results.tex`: ready-made
  five-model summaries. The previously published four-model paper figure is unchanged.
- `manifest.json`: dataset/result provenance hashes, counts and file checksums.

Read compressed CSVs with `gzip.open(path, 'rt', encoding='utf-8')` plus
`csv.DictReader`, or `pandas.read_csv(path)`.

The binding hash is `scripts.final_benchmark.api.digest` of a dictionary with
`case_id`, `query`, `answer`, `query_language`, `answer_language`, `image_language`,
`image_sha256`, and `source_context` (missing fields use `None`). Before comparing
new models, verify the same frozen inputs, seed IDs and language tuples. Do not
join by row number, infer flips from aggregate ACC, or change failed judgments.
Duplicate model/configuration keys must be rejected rather than averaged.

## Scope and limitations

This is a **compact frozen-score export**, not a raw inference run directory.
Do not place it directly into `configs/paired_runs.json`, whose validator expects
complete request/prediction/Judge artifacts. Use the CSVs for offline aggregation
with the other machine's evaluated models. Existing `plot()` accepts any number
of models through its row records; it does not call APIs.

The export excludes raw answers, request/response bodies, credentials, image
files and absolute local paths. It supports reproducing scoring-based analyses,
not independently re-adjudicating answers. Historical generation settings and
format fallback remain as evaluated. Full local provenance was validated before
export; the source hashes allow later reconciliation without distributing logs.

To regenerate locally after running `paired_analysis` on the chosen model list:

```sh
python -m scripts.evaluation.export_frozen_results \
  --analysis /path/to/validated/paired_analysis \
  --output results/frozen_20261002
```
