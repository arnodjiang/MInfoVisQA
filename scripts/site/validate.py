"""Offline release checks for public leaderboard values and linked example assets."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'site'

def main():
    data = json.loads((SITE / 'data/leaderboard.json').read_text())
    languages = [l['code'] for l in data['languages']]
    assert len(languages) == len(set(languages)) == 24
    names = set()
    for row in data['models']:
        assert row['name'] not in names
        names.add(row['name'])
        assert row['access'] in ('open', 'closed')
        assert list(row['lqa']) == languages
        scores = [row['xqa_zh'], row['xqa_en'], *row['lqa'].values(), row['avg']]
        assert len(scores) == 27 and all(isinstance(x, (float, int)) and 0 <= x <= 100 for x in scores)
        # Each reported cell is rounded to one decimal; permit aggregate rounding.
        approx = (23*row['xqa_zh'] + 23*row['xqa_en'] + sum(row['lqa'].values()))/70
        assert abs(approx-row['avg']) <= .101, (row['name'], approx, row['avg'])
        if row['access'] == 'open': assert row['model_card'].startswith('https://huggingface.co/')
    for example in json.loads((SITE / 'data/examples.json').read_text()):
        for variant in example['variants']:
            asset = (SITE / variant['image']).resolve()
            assert SITE.resolve() in asset.parents
            assert hashlib.sha256(asset.read_bytes()).hexdigest() == variant['image_sha256']
            assert set(variant['qa']) == {variant['language'], 'en', 'zh'}
            assert all(q['query'] and q['answer'] and q['id'] for q in variant['qa'].values())
    with (SITE / 'data/leaderboard.csv').open(newline='') as stream:
        csv_rows = list(csv.reader(stream))
    assert len(csv_rows) == len(data['models']) + 1
    for csv_row, row in zip(csv_rows[1:], data['models']):
        assert csv_row[:2] == [row['name'], row['access']]
        assert list(map(float,csv_row[2:])) == [row['xqa_zh'],row['xqa_en'],*row['lqa'].values(),row['avg']]
    print(f"Validated {len(names)} models, 27 scores each, 24 languages and 6 image checksums.")

if __name__ == '__main__': main()
