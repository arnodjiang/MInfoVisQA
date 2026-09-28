'use strict';
const $ = (s) => document.querySelector(s);
const state = {data: null, examples: null, filter: 'all', view: 'overview', search: '', sort: 'avg', desc: true};
function el(tag, text, className) { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (className) n.className = className; return n; }
function score(model, key) {
  if (key === 'name') return model.name;
  if (key === 'lqa_mean') return Object.values(model.lqa).reduce((a,b) => a+b, 0) / 24;
  if (key.startsWith('lqa_')) return model.lqa[key.slice(4)];
  return model[key];
}
function columns() {
  const main = [['name','Model'],['xqa_zh','XQA · ZH'],['xqa_en','XQA · EN']];
  return [...main, ...(state.view === 'overview' ? [['lqa_mean','LQA · mean']] : state.data.languages.map(l => ['lqa_'+l.code,l.code])), ['avg','AVG']];
}
function selectedModels() {
  return state.data.models.filter(m => (state.filter === 'all' || state.filter === m.access) && m.name.toLowerCase().includes(state.search.toLowerCase())).sort((a,b) => {
    const av=score(a,state.sort), bv=score(b,state.sort);
    const cmp=typeof av === 'string' ? av.localeCompare(bv) : av-bv;
    return (state.desc ? -cmp : cmp) || a.name.localeCompare(b.name);
  });
}
function renderTable() {
  const cols=columns(), models=selectedModels(), head=el('tr');
  const rank=el('th','#'); rank.scope='col'; head.append(rank);
  for (const [key,label] of cols) {
    const th=el('th');th.scope='col';th.setAttribute('aria-sort',state.sort===key ? (state.desc?'descending':'ascending'):'none');
    const button=el('button',label);button.type='button';button.dataset.sort=key;
    if(key.startsWith('lqa_') && key!=='lqa_mean') button.title='LQA · '+state.data.languages.find(l=>l.code===key.slice(4)).name;
    const arrow=el('span',state.sort===key ? (state.desc?'↓':'↑'):'↕','sort-indicator'); arrow.setAttribute('aria-hidden','true');button.append(arrow);
    button.addEventListener('click',()=>{if(state.sort===key) state.desc=!state.desc;else {state.sort=key;state.desc=key!=='name';}renderTable(); const focusButton=[...$('#scores-head').querySelectorAll('button')].find(b=>b.dataset.sort===key);focusButton.focus({preventScroll:true});});
    th.append(button);head.append(th);
  }
  $('#scores-head').replaceChildren(head); const body=$('#scores-body');body.replaceChildren();
  $('#scores-table').classList.toggle('language-table',state.view==='languages');
  if(!models.length) { const tr=el('tr'),td=el('td','No matching models. Try another name or access filter.','empty');td.colSpan=cols.length+1;tr.append(td);body.append(tr); }
  const ranks = [...state.data.models].sort((a,b)=>b.avg-a.avg);
  for (const m of models) {
    const tr=el('tr');tr.append(el('td',String(ranks.indexOf(m)+1).padStart(2,'0')));
    for (const [key] of cols) {
      const td=el('td');
      if(key==='name') {
        const b=el('button',m.name,'model-name');b.type='button';b.addEventListener('click',()=>showModel(m));td.append(b,el('span',m.access==='open'?'Open weights':'Closed model','model-meta '+m.access));
      } else {
        const v=score(m,key);td.textContent=v.toFixed(1);
        if(v===Math.max(...state.data.models.map(x=>score(x,key))))td.classList.add('best-score');
        if(key==='avg'){td.classList.add('avg-cell');const bar=el('span',undefined,'score-bar'),fill=el('i');fill.style.width=v+'%';bar.setAttribute('aria-hidden','true');bar.append(fill);td.append(bar);}
      }
      tr.append(td);
    }
    body.append(tr);
  }
  $('#result-count').textContent=`${models.length} of ${state.data.models.length} models · ${state.view==='overview'?'click a metric to sort':'scroll for all languages →'}`;
}
function showModel(m) {
  $('#model-title').textContent=m.name;const body=$('#model-details');body.replaceChildren();
  body.append(el('p',`${m.access==='open'?'Open weights':'Closed model'} · Reported AVG ${m.avg.toFixed(1)}%`));
  body.append(el('p',state.data.source));body.append(el('p',state.data.protocol));
  body.append(el('p','Model names are reported API identifiers. Provider deployments and decoding settings may differ. Scores are not independently verified by this website.'));
  if(m.model_card){const a=el('a','Official model card & weight availability ↗');a.href=m.model_card;a.target='_blank';a.rel='noopener';body.append(a);}
  $('#model-dialog').showModal();
}
function renderMatrix() {
  const grid=$('#configuration-matrix');grid.classList.add('matrix-grid');
  state.data.languages.forEach((q,i)=>state.data.languages.forEach((v,j)=>{
    const cell=el('span');let category='not evaluated';
    if(i===j){cell.className='matrix-cell lqa';category='LQA';}else if(q.code==='ZH'){cell.className='matrix-cell zh';category='XQA-ZH';}else if(q.code==='EN'){cell.className='matrix-cell en';category='XQA-EN';}else cell.className='matrix-cell';
    cell.title=`${category}: visual ${v.code}, question & answer ${q.code}`;cell.setAttribute('aria-hidden','true');grid.append(cell);
  }));
}
function renderGallery() {
  const ex=state.examples[Number($('#example-case').value)];
  const gallery=$('#example-gallery');gallery.replaceChildren();
  for(const variant of ex.variants){
    const language=state.data.languages.find(l=>l.code.toLowerCase()===variant.language);
    const button=el('button',null,'gallery-card');button.type='button';button.dataset.language=variant.language;
    button.setAttribute('aria-label','View '+language.name+' example');
    const image=el('img');image.src=variant.image;image.alt=ex.visual_kind+' in '+language.name;image.loading='lazy';image.decoding='async';
    button.append(image,el('span',language.code+' · '+language.name));
    button.addEventListener('click',()=>{$('#example-language').value=variant.language;renderExample();});
    gallery.append(button);
  }
}
function renderExample() {
  const ex=state.examples[Number($('#example-case').value)],lang=$('#example-language').value,setting=$('#example-setting').value;
  const variant=ex.variants.find(v=>v.language===lang),queryLang=setting==='lqa'?lang:setting,qa=variant.qa[queryLang];
  const img=$('#example-image');img.src=variant.image;img.alt=`${ex.visual_kind} in ${lang.toUpperCase()}, localized from ${ex.source}; case ${ex.case_id}`;
  $('#example-image-link').href=variant.image;$('#example-question').textContent=qa.query;$('#example-question').lang=queryLang;
  $('#example-answer').textContent=qa.answer;$('#example-answer').lang=queryLang;$('#answer-reveal').open=false;
  $('#example-type').textContent=`${lang===queryLang?'LQA':'XQA-'+queryLang.toUpperCase()} · visual ${lang.toUpperCase()} → QA ${queryLang.toUpperCase()}`;
  document.querySelectorAll('.gallery-card').forEach(b=>{const selected=b.dataset.language===lang;b.classList.toggle('selected',selected);b.setAttribute('aria-pressed',String(selected));});
  $('#example-source').textContent=ex.source+' · '+ex.visual_kind;$('#example-id').textContent='Case '+ex.case_id;
}
async function loadJSON(url){const r=await fetch(url);if(!r.ok)throw new Error(`Unable to load ${url} (${r.status})`);return r.json();}
async function init(){
  try {
    state.data=await loadJSON('data/leaderboard.json');
    for(const l of state.data.languages){const chip=el('span',l.code,'lang-chip');chip.title=l.name;chip.setAttribute('aria-label',l.name);$('#language-chips').append(chip);}
    document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{state.filter=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});renderTable();}));
    document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{state.view=b.dataset.view;if(!columns().some(([k])=>k===state.sort)){state.sort='avg';state.desc=true;}document.querySelectorAll('[data-view]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});renderTable();}));
    $('#model-search').addEventListener('input',e=>{state.search=e.target.value;renderTable();});
    $('.dialog-close').addEventListener('click',()=>$('#model-dialog').close());
    renderTable();renderMatrix();
    state.examples=await loadJSON('data/examples.json');
    $('#example-language').replaceChildren(...state.data.languages.map(l=>{const option=el('option',l.code+' · '+l.name);option.value=l.code.toLowerCase();return option;}));
    renderGallery();renderExample();
    $('#example-case').addEventListener('change',()=>{renderGallery();renderExample();});
    ['example-language','example-setting'].forEach(id=>$('#'+id).addEventListener('change',renderExample));
  } catch(error){$('#load-error').hidden=false;$('#load-error').textContent=error.message+'. Reload the page or download the results JSON.';$('#result-count').textContent='Data could not be loaded';}
}
init();
