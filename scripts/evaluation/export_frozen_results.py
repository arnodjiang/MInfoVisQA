"""Export shareable correctness records, never API credentials or request/response logs.

Requires a completed paired_analysis output, whose hashes are rechecked here.
No predictions or judgments are changed and no model APIs are called.
"""
import argparse,csv,gzip,io,json
from pathlib import Path
from scripts.evaluation.paired_analysis import ROOT,DEFAULT_DATA,read,indexed,sha
from scripts.final_benchmark.api import digest
from scripts.evaluation.score import LANGUAGES

def csv_file(path,rows,compressed=False):
    text=io.StringIO(newline='');w=csv.DictWriter(text,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    blob=text.getvalue().encode()
    path.write_bytes(gzip.compress(blob,mtime=0) if compressed else blob)

def export(args):
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    validation=read(args.analysis/'input_validation.json');metrics=read(args.analysis/'paired_metrics.json')
    if sha(args.dataset)!=metrics['dataset_sha256']:raise ValueError('Dataset changed since validation')
    data=indexed(args.dataset)
    configs=[]
    for rid,r in sorted(data.items()):
        bound={k:r.get(k) for k in ['case_id','query','answer','query_language','answer_language','image_language','image_sha256','source_context']}
        configs.append({'id':rid,'case_id':r['case_id'],'visual_language':r['image_language'],'query_language':r['query_language'],'answer_language':r['answer_language'],'visual_family':r['visual_family'],'visual_kind':r['visual_kind'],'input_binding_sha256':digest(bound)})
    scores=[];models=[];correctness={}
    for model,v in validation.items():
        path=Path(v['run']);run=path if path.is_absolute() else ROOT/path
        if not run.exists():run=ROOT/'data/evaluation'/path
        jd=run/'llm_judge_text_v2'
        if sha(run/'references.jsonl')!=v['references_sha256'] or sha(jd/'judgments.jsonl')!=v['judgments_sha256']:raise ValueError('Frozen input changed after validation')
        refs=indexed(run/'references.jsonl');judges=indexed(jd/'judgments.jsonl')
        if set(refs)!=set(data) or set(judges)!=set(data):raise ValueError('Incomplete model')
        jp=(jd/'prompt.txt').read_text();corrections=read(jd/'reference_corrections.json')
        from scripts.evaluation.reference_corrections import corrected_reference
        for rid,r in sorted(refs.items()):
            p=read(run/'predictions'/f'{rid}.json');j=judges[rid]
            if j['input_fingerprint']!=digest([r,p,corrected_reference(r,corrections),digest(jp)]):raise ValueError('Prediction or judgment changed')
            y=int(p['status']=='completed' and j['verdict']=='equivalent')
            scores.append({'model':model,'id':rid,'correct':y,'prediction_status':p['status'],'judge_method':j['method'],'verdict':j['verdict']})
            correctness[model,r['case_id'],r['query_language'],r['image_language']]=y
        models.append({'name':model,'configurations':len(refs),'references_sha256':v['references_sha256'],'judgments_sha256':v['judgments_sha256'],'judge_model':v['judge_manifest']['judge_model'],'judge_prompt_sha256':digest(jp)})
    seedrows=[]
    for model in validation:
        for cid in sorted({r['case_id'] for r in data.values()}):
            r=next(r for r in data.values() if r['case_id']==cid)
            for q in ['en','zh']:
                seedrows.append({'model':model,'case_id':cid,'query_language':q,'visual_family':r['visual_family'],'visual_kind':r['visual_kind'],**{v:correctness[model,cid,q,v] for v in LANGUAGES}})
    csv_file(out/'configuration_bindings.csv.gz',configs,True)
    csv_file(out/'frozen_correctness.csv.gz',scores,True)
    csv_file(out/'paired_seed_correctness.csv',seedrows)
    # Only numerical summaries and explicitly public classification metadata.
    clean={k:metrics[k] for k in ['schema','dataset_sha256','bootstrap','metric_order','frozen_result_policy','classification_review']}
    clean['models']={m:{q:x[q] for q in ['en','zh']} for m,x in metrics['models'].items()}
    (out/'paired_metrics.json').write_text(json.dumps(clean,ensure_ascii=False,indent=2)+'\n')
    for name in ['coverage_curves.csv','subgroup_metrics.csv','paired_results.tex']:(out/name).write_bytes((args.analysis/name).read_bytes().replace(b'\r\n',b'\n'))
    files={p.name:sha(p) for p in out.iterdir() if p.name!='manifest.json' and p.name!='README.md' and p.is_file()}
    manifest={'schema':'minfovisqa-frozen-correctness-v1','models':models,'dataset_sha256':sha(args.dataset),'n_seeds':128,'configurations_per_seed':70,'configurations_per_model':8960,'total_correctness_records':len(scores),'paired_seed_rows':len(seedrows),'visual_language_order':LANGUAGES,'policy':'Frozen semantic correctness; original failures retained; no reruns, exclusion, or new judging. Strict match followed by existing text-only Judge.','usage':'Join full scores to configuration bindings by id; join new models by matching case_id and language tuple after verifying input bindings. paired_seed_correctness already provides EN/ZH 24-visual clusters.','files_sha256':files}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'models':list(validation),'correctness_records':len(scores),'paired_seed_rows':len(seedrows),'output':str(out)}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analysis',type=Path,required=True);p.add_argument('--dataset',type=Path,default=DEFAULT_DATA);p.add_argument('--output',type=Path,default=ROOT/'results/frozen_20261002');export(p.parse_args())
