"""Sync all published cells from a frozen copy of the manuscript main table."""
import json,re,csv,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'site/data'
def parse(text):
    rows=[];group='';access='closed'
    for chunk in text.split(r'\\'):
        if 'Proprietary MLLMs' in chunk:group='Proprietary MLLMs';access='closed'
        elif 'General-purpose Open-source MLLMs' in chunk:group='General-purpose Open-source MLLMs';access='open'
        elif 'Chart-specialized MLLMs' in chunk:group='Chart-specialized MLLMs';access='open'
        m=re.search(r'([A-Za-z][A-Za-z0-9.\-]+)\s*&\s*(\d+\.\d+.*)',chunk,re.S)
        if m:
            vals=[float(v) for v in re.findall(r'\d+\.\d+',m[2])];assert len(vals)==27,(m[1],len(vals))
            rows.append((m[1],access,group,vals))
    assert len(rows)==25
    return rows
def main():
    p=DATA/'leaderboard.json';d=json.loads(p.read_text());old={x['name']:x for x in d['models']};langs=[l['code'] for l in d['languages']]
    d['models']=[]
    for name,access,group,v in parse((DATA/'paper-main-table.tex').read_text()):
        r={'name':name,'access':access,'group':group,'model_card':old.get(name,{}).get('model_card'),'xqa_zh':v[0],'xqa_en':v[1],'lqa':dict(zip(langs,v[2:26])),'avg':v[26],'result_source':'Current manuscript main table','judge':'GPT-6 Astra','note':'All 27 scores transcribed unchanged from the manuscript. Model grouping follows the paper; links retained only where already documented.'};d['models'].append(r)
    d['updated']='2026-10-13';d['source']='Current manuscript main table: 25 models, 27 published scores per model. Frozen source: site/data/paper-main-table.tex. Scores and model groups are supplied by the authors.'
    d['source_sha256']=hashlib.sha256((DATA/'paper-main-table.tex').read_bytes()).hexdigest();p.write_text(json.dumps(d,indent=2)+'\n')
    with (DATA/'leaderboard.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Model','Access','XQA-ZH','XQA-EN',*['LQA-'+l for l in langs],'AVG'])
        for r in d['models']:w.writerow([r['name'],r['access'],r['xqa_zh'],r['xqa_en'],*r['lqa'].values(),r['avg']])
if __name__=='__main__':main()
