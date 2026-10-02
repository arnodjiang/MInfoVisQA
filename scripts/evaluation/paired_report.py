"""Publish offline paired diagnostics as manuscript fragments and a source-control review manifest."""
import argparse, json
from pathlib import Path
from scripts.evaluation.paired_analysis import ROOT, RUNS, DEFAULT_DATA, indexed, read, sha
from scripts.evaluation.context_input import input_text

OUT=ROOT/'outputs/paired_analysis'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUT)
    parser.add_argument("--source-preflight",action="store_true",help="Optional local archive check; never calls model APIs")
    args=parser.parse_args()
    out=args.output
    report=read(out/'paired_metrics.json')
    tables=ROOT/'paper/tables';tables.mkdir(exist_ok=True)
    (tables/'paired_results.tex').write_text((out/'paired_results.tex').read_text())
    appendix=[]
    groups=[('all','All'),('chart','Charts'),('table','Tables'),('simple_table','Simple tables'),('spanning_table','Spanning tables'),('composite_table','Composite table')]
    for name,m in report['models'].items():
        extra=[g for g in m['en'] if g not in {x[0] for x in groups} and g not in ['complete_seed_sensitivity','failure_free_sensitivity','coverage']]
        labels={'invariant':'No translation required','language_bearing':'Translatable text'}
        current=groups+[(g,labels.get(g,g.replace('_',' '))) for g in extra]
        header=r'''\begin{table*}[t]
\centering\scriptsize
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrrrr@{}}
\toprule
Subset & Q & $n$ & Baseline & Cross-visual & $\Delta$ACC [95\% CI] & C$\to$W & W$\to$C \\
\midrule
'''
        tex=header
        for group,label in current:
            for q in ['en','zh']:
                a=m[q][group];v=a['point'];lo,hi=a['ci95'][2]
                tex+=f"{label} & {q.upper()} & {a['n_seeds']} & {v[0]:.1f} & {v[1]:.1f} & {v[2]:+.1f} [{lo:+.1f}, {hi:+.1f}] & {v[3]:.1f} & {v[4]:.1f}"+r' \\'+'\n'
        tex+=r'\bottomrule\end{tabular*}'+'\n'+r'\caption{'+name+r''': paired subgroup analysis. ACC and flip rates are percentages; differences are percentage points. Flip denominators are $23n$ within each subset. Seed-cluster bootstrap uses 10,000 draws. The single composite table supports only a descriptive case result; its degenerate interval is not evidence of population certainty. Answer groups reuse the existing translation audit.}
\end{table*}
'''
        appendix.append(tex)
    (tables/'paired_subgroups.tex').write_text('\n'.join(appendix))
    if args.source_preflight:
        # Preserve source images; do not equate byte-verified provenance with semantic eligibility.
        refs={r['case_id']:r for r in indexed(DEFAULT_DATA).values() if r['image_language']==r['query_language']=='en'}
        lineage=read(ROOT/'data/evaluation'/RUNS[0][1]/'lineage/latest.json')
        snapshot=Path(lineage['snapshot']['archive_path']);assert sha(snapshot)==lineage['snapshot']['sha256']
        rows=[]
        for s in read(snapshot)['source_records']:
            r=refs[s['case_id']];image=s.get('upstream_image');available=s['original_visual_status']=='available'
            if available:assert sha(image['archive_path'])==image['sha256']
            current=(DEFAULT_DATA.parent/r['image_path']).resolve();assert sha(current)==r['image_sha256']
            rows.append({'case_id':r['case_id'],'current_id':r['id'],'source':r['source'],'original_available':available,'original_image':image if available else None,'reconstructed_image':{'path':str(current),'sha256':r['image_sha256']},'question':r['query'],'input_text':input_text(r),'reference':r['answer'],'source_context':r.get('source_context'),'upstream_question':s['upstream_question'],'upstream_answer':s['upstream_answer'],'question_text_identical':r['query']==s['upstream_question'],'eligibility':'agent_visual_checked_for_smoke_only' if r['case_id']=='2bf86a8ac478956722f8' else ('requires_shared_references_and_answerability_review' if available else 'excluded_no_original_raster')})
        (out/'original_control_manifest.json').write_text(json.dumps({'schema':'original-control-preflight-v1','historical_reconstruction_reuse':False,'execution_policy':'Disabled at user request: no new inference or Judge calls','reason':'User confirmed frozen scores and explicitly cancelled reruns. This manifest records source availability only.','available_originals':sum(x['original_available'] for x in rows),'authorized_new_inference_calls':0,'aggregate_experiment_status':'cancelled_by_user','records':rows},ensure_ascii=False,indent=2)+'\n')
    (ROOT/'paper/paired_analysis_results.tex').write_text(r'''% Insert after the main performance table; not a standalone document.
\subsection{Paired Sensitivity to Visual-Language Changes}
We hold the question, reference answer, and optional source context fixed in English or Chinese and vary the visual language across 24 versions of each seed. The corresponding same-language visual provides the baseline. We report the mean accuracy difference and both directions of correctness flips, using all $128\times23$ cross-language pairs as the denominator for each question language. Confidence intervals resample the 128 seeds with all their language variants, using 10,000 bootstrap draws.

\input{paper/tables/paired_results}
Average accuracy can conceal opposing changes at the instance level. For Gemini-3.8-Flash with Chinese questions, the net change is only $-0.03$ percentage points, yet 2.92\% of pairs change from correct to wrong and 2.89\% change from wrong to correct. GPT-5.6-Luna shows a similar cancellation: a net change of $-0.54$ points comprises 6.39\% correct-to-wrong and 5.84\% wrong-to-correct flips. GPT-6 Astra instead exhibits a net decline for both English ($-4.21$ points; 95\% CI $[-7.13,-1.83]$) and Chinese ($-4.82$; $[-9.04,-0.92]$). These are descriptive comparisons of visual-language versions, which can differ in font and layout as well as text; they do not isolate OCR or language understanding.

The correct-coverage curves further distinguish average performance from reliability across languages. With English questions, the fraction of seeds answered correctly in all 24 visual languages is 70.3\% for GPT-6 Astra and Gemini-3.8-Flash, 57.0\% for GPT-5.6-Sol, and 39.1\% for GPT-5.6-Luna. The corresponding Chinese values are 67.2\%, 64.8\%, 49.2\%, and 42.2\%. Each configuration was evaluated once: these curves include generation and judging variability and do not estimate test--retest reliability.

All analyses reuse the frozen main-table predictions and judgments, including the original treatment of failed requests. No configurations are repaired, rerun, or excluded. Nominal prompts are verified across all variants; historical generation-setting changes and format-only fallback are retained, and some legacy attempts lack effective-prompt hashes. The results therefore describe paired sensitivity under the recorded evaluation protocol, rather than a perfectly uniform historical inference protocol.

% Upload outputs/paired_analysis/cross_language_coverage.pdf to Overleaf img/.
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{img/cross_language_coverage.pdf}
\caption{Cross-language correct coverage for fixed English (left) and Chinese (right) questions and answers. At threshold $k$, the ordinate is the percentage of 128 seeds answered correctly in at least $k$ of the 24 visual languages. The right endpoint requires every visual-language variant to be correct.}
\label{fig:cross-language-coverage}
\end{figure*}
''')
    # Self-contained table preview: no external dependencies beyond standard packages.
    preview=r'''\documentclass[10pt]{article}
\usepackage[textwidth=6.3in,margin=1in]{geometry}
\usepackage{booktabs,multirow}
\begin{document}
'''+(tables/'paired_results.tex').read_text().replace(r'\small',r'\scriptsize')+'\n'+r'\end{document}'+'\n'
    (ROOT/'paper/paired_results_preview.tex').write_text(preview)
    print('Wrote manuscript fragments. Source preflight runs only when explicitly requested.')

if __name__=='__main__':main()
