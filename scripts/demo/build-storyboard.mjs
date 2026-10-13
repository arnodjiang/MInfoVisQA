import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=process.cwd(),sk=process.env.PRESENTATIONS_SKILL_DIR;
if(!sk) throw new Error('Set PRESENTATIONS_SKILL_DIR to the installed Presentations skill');
const {applyPresentationChartFont,finalizePresentation}=await import(sk+'/container_tools/artifact_tool_utils.mjs');
const scenes=JSON.parse(await fs.readFile('build/demo/scenes.json')),e=JSON.parse(await fs.readFile('site/assets/demo/evidence.json'));
const deck=Presentation.create({slideSize:{width:1920,height:1080}});
for(let i=0;i<scenes.length;i++){
 const slide=deck.slides.add();slide.background.fill='#F6F8FA';
 for(const o of scenes[i]){
  if(o.type==='text'){
   const s=slide.shapes.add({geometry:'textbox',position:{left:o.x,top:o.y,width:Math.min(o.w+12,1910-o.x),height:o.h},fill:'none',line:{fill:'none',width:0}});s.text=o.text;s.text.style={fontSize:o.size,typeface:o.title?'Comic Sans MS':'Times New Roman',bold:o.bold,color:o.color,wrap:'none',insets:0,autoFit:'none'};
  }else if(o.type==='box'){
   const [x,y,x2,y2]=o.rect;slide.shapes.add({geometry:'roundRect',position:{left:x,top:y,width:x2-x,height:y2-y},fill:o.fill,line:{fill:'none',width:0}});
  }else if(o.type==='image'){
   const [x,y,w,h]=o.rect;slide.images.add({blob:await fs.readFile(path.join(root,o.path)),contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit:'contain',alt:o.path});
  }else if(o.type==='line'){
   for(let j=1;j<o.pts.length;j++){
    const [x,y]=o.pts[j-1],[xx,yy]=o.pts[j],len=Math.hypot(xx-x,yy-y),angle=Math.atan2(yy-y,xx-x)*180/Math.PI;
    slide.shapes.add({geometry:'rect',position:{left:(x+xx-len)/2,top:(y+yy-o.width)/2,width:len,height:o.width,rotation:angle},fill:o.color,line:{fill:'none',width:0}});
   }
  }
 }
 if(i===4){
  const names=['GPT-6-Astra','Gemini-3.8-Flash','GPT-5.6-Luna','Qwen3.5-9B'],colors=['#925EA7','#327D83','#154677','#C99E48'];
  const c=slide.charts.add('radar',{position:{left:168,top:290,width:786,height:670},categories:e.performance.languages,series:names.map((n,j)=>({name:n,values:e.performance.models.find(m=>m.model===n).lqa,fill:'none',line:{fill:colors[j],width:3}})),hasLegend:false,radarOptions:{style:'standard'},chartFill:'none',plotAreaFill:'none',xAxis:{textStyle:{fontSize:26,fill:'#154677'}},yAxis:{min:0,max:100,majorUnit:20,textStyle:{fontSize:20,fill:'#607582'},majorGridlines:{fill:'#CFDCE3',width:1}}});applyPresentationChartFont(c,{fontFamily:'Times New Roman',availableFonts:['Times New Roman','Comic Sans MS']});
 }
 slide.speakerNotes.text='Sources: https://huggingface.co/datasets/arnodjiang/MInfoVisQA ; site/assets/demo/evidence.json and transcript.html. Scene '+(i+1)+' of the 46-second research demonstration. Real images are independent replaceable objects. Text and shapes editable; radar native chart. Observed EN/JA case is one recorded pair; radar is LQA, distinct from fixed-English example.';
}
await (await PresentationFile.exportPptx(deck)).save('build/demo/candidate.pptx');
await finalizePresentation({workspaceDir:root,candidatePath:root+'/build/demo/candidate.pptx',finalPath:root+'/site/assets/demo/MInfoVisQA-demo-storyboard.pptx',pythonExecutable:process.env.RUNTIME_PYTHON || 'python3',integrityValidatorPath:sk+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:sk+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','18288000,10287000'],explicitTotalSlideCount:6,requiredNativeChartOwnerSlides:[5],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'user_request',families:['Comic Sans MS','Times New Roman']},verifyArtifactToolImport:true,receiptPath:root+'/build/demo/validation.json'});
