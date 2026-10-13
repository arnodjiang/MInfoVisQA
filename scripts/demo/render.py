"""Deterministic, editable Pillow/FFmpeg demo. Run from any directory.
Requires Pillow; FFmpeg on PATH. Fonts: Comic Sans MS and Times New Roman.
All sample images are unmodified dataset assets; animations are presentation only.
"""
from pathlib import Path
import json, math, subprocess, hashlib, os
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'site/assets/demo'
W,H,FPS=1920,1080,24
DUR=[5,8,8,9,10,6]; START=[sum(DUR[:i]) for i in range(6)]
NAVY='#154677'; TEAL='#327D83'; GOLD='#C99E48'; PURPLE='#925EA7'; INK='#203849'; MUTED='#607582'; BG='#F6F8FA'
FONTS=Path(os.environ.get('DEMO_FONT_DIR','/System/Library/Fonts/Supplemental'))
font_cache={}
def font(size,bold=False,title=False):
 key=(size,bold,title)
 if key not in font_cache:
  name=('Comic Sans MS'+(' Bold' if bold else '') if title else 'Times New Roman'+(' Bold' if bold else ''))+'.ttf'
  font_cache[key]=ImageFont.truetype(str(FONTS/name),size)
 return font_cache[key]
def txt(im,xy,s,size=32,color=INK,bold=False,title=False):ImageDraw.Draw(im).text(xy,s,font=font(size,bold,title),fill=color)
def line(im,pts,c=TEAL,w=3):ImageDraw.Draw(im).line(pts,fill=c,width=w)
def box(im,rect,fill='white',r=24,outline=None):ImageDraw.Draw(im).rounded_rectangle(rect,r,fill=fill,outline=outline,width=2)
def base(n):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.ellipse((1370,-540,2380,470),fill='#EBF2F3');d.ellipse((-270,760,310,1340),fill='#F4EBD8')
 txt(im,(72,36),'MInfoVisQA',30,NAVY,True,True)
 txt(im,(1440,44),'SAME INFORMATION / NEW LANGUAGE',21,MUTED)
 line(im,[(72,91),(1848,91)],'#CFDCE3',2)
 txt(im,(72,1026),'Charts + visual tables  /  24 languages',23,MUTED)
 txt(im,(1700,1026),f'{n+1:02d} / 06',23,MUTED)
 return im
cache={}
def asset(path):
 path=str(path)
 if path not in cache:cache[path]=Image.open(path).convert('RGB')
 return cache[path]
def fit(im,path,rect):
 src=asset(path);x,y,w,h=rect;ratio=min(w/src.width,h/src.height);sz=(int(src.width*ratio),int(src.height*ratio));key=(str(path),sz)
 if key not in cache:cache[key]=src.resize(sz,Image.Resampling.LANCZOS)
 im.paste(cache[key],(int(x+(w-sz[0])/2),int(y+(h-sz[1])/2)))
def check(im,x,y,good):
 d=ImageDraw.Draw(im);c=TEAL if good else '#B95850';d.ellipse((x,y,x+54,y+54),fill='#DDEEE9' if good else '#F5E3E0')
 if good:line(im,[(x+14,y+28),(x+24,y+37),(x+41,y+16)],c,5)
 else:
  line(im,[(x+17,y+17),(x+37,y+37)],c,5);line(im,[(x+17,y+37),(x+37,y+17)],c,5)
def sample_card(im,lang,x,y,w,h,outcome=False):
 box(im,(x,y,x+w,y+h));txt(im,(x+28,y+18),'English visual' if lang=='en' else 'Japanese visual',30,NAVY,True)
 fit(im,OUT/f'case-{lang}.png',(x+20,y+68,w-40,h-160 if outcome else h-90))
 if outcome:
  txt(im,(x+30,y+h-78),'Winter' if lang=='en' else 'Autumn',45,TEAL if lang=='en' else '#B95850',True)
  check(im,x+w-90,y+h-75,lang=='en')
def header(im,a,b=None):
 txt(im,(72,124),a,60,NAVY,True,True)
 if b:txt(im,(76,211),b,32,MUTED)
e=json.loads((OUT/'evidence.json').read_text());perf=e['performance'];langs=perf['languages']
selected=[next(x for x in perf['models'] if x['model']==n) for n in ['GPT-6-Astra','Gemini-3.8-Flash','GPT-5.6-Luna','Qwen3.5-9B']]
COLORS=[PURPLE,TEAL,NAVY,GOLD]
def scene(n,t):
 im=base(n)
 if n==0:
  txt(im,(76,164),'Same information.',88,NAVY,True,True);txt(im,(76,280),'Different language.',88,TEAL,True,True)
  txt(im,(80,441),'Can a model still find the same answer?',45,INK)
  box(im,(78,569,917,807));txt(im,(112,600),'MInfoVisQA',58,NAVY,True,True)
  txt(im,(112,691),'A multilingual benchmark for',35);txt(im,(112,738),'information-rich visual question answering',35)
  fit(im,ROOT/'site/assets/6c1b80891d9f43724aa6-en.png',(985,215,855,585))
  txt(im,(1070,841),'Real benchmark images. Recorded results.',29,MUTED)
 elif n==1:
  header(im,'One chart. One question.','On average, which season records the highest number of breakups?')
  lang='en' if t<4 else 'ja'
  sample_card(im,lang,83,294,1240,665,outcome=t>=2)
  txt(im,(1390,360),'QUESTION',25,MUTED);txt(im,(1390,410),'English',47,NAVY,True)
  txt(im,(1390,520),'MODEL',25,MUTED);txt(im,(1390,570),'GPT-5.6-Luna',35,NAVY,True)
  txt(im,(1390,679),'REFERENCE',25,MUTED);txt(im,(1390,725),'Winter',47,TEAL,True)
  txt(im,(1390,846),'Only the visual',31);txt(im,(1390,891),'language changes.',31)
 elif n==2:
  header(im,'A language switch. A different answer.','Same seed, same English question, same model and recorded run.')
  sample_card(im,'en',76,292,855,597,True);sample_card(im,'ja',989,292,855,597,True)
  txt(im,(80,918),'Reference: Winter  |  Observed example; not a general language ranking.',30,MUTED)
  txt(im,(80,965),'ChartQAPro source case: 32a59a1788ab3cc9f351',23,MUTED)
 elif n==3:
  header(im,'Beyond a single chart.','Parallel chart and visual-table images preserve numerical content and structure.')
  lang=['en','zh','ja','ar'][min(3,int(t/2.25))];names={'en':'English','zh':'Chinese','ja':'Japanese','ar':'Arabic'}
  for x,cid,label in [(76,'6c1b80891d9f43724aa6','ChartQA / grouped bars'),(989,'345c918a890d9cdd8b8f','TableVQA-Bench / visual table')]:
   box(im,(x,295,x+855,811));txt(im,(x+26,313),label,30,NAVY,True);fit(im,ROOT/f'site/assets/{cid}-{lang}.png',(x+20,372,815,406))
  txt(im,(76,838),'Visual language: '+names[lang],33,TEAL,True)
  for i,l in enumerate(langs):
   x=76+(i%12)*148;y=901+(i//12)*48
   box(im,(x,y,x+130,y+39),TEAL if l.lower()==lang else '#E5ECEF',10)
   txt(im,(x+43,y+3),l,26,'white' if l.lower()==lang else NAVY)
 elif n==4:
  header(im,'Language profiles reveal the variation.','LQA accuracy (%) / question and answer language match the visual language.')
  cx,cy,r=560,613,282;draw=ImageDraw.Draw(im)
  for radius,c in [(r,'#E7EBF3'),(r*.8,'#ECF4F1'),(r*.6,'#F5EDDE'),(r*.4,'#F7F4EB'),(r*.2,'white')]:draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=c,outline='#CBD7DF',width=2)
  for i,l in enumerate(langs):
   a=-math.pi/2+2*math.pi*i/24;x=cx+math.cos(a)*r;y=cy+math.sin(a)*r;line(im,[(cx,cy),(x,y)],'#D1DCE1',1)
   tx=cx+math.cos(a)*(r+38);ty=cy+math.sin(a)*(r+38);txt(im,(tx-16,ty-15),l,26,NAVY)
  for val in [20,40,60,80,100]:txt(im,(cx+7,cy-r*val/100-20),str(val),19,MUTED)
  for j,m in reversed(list(enumerate(selected))):
   scale=min(1,max(0,t/1.5));pts=[(cx+math.cos(-math.pi/2+2*math.pi*i/24)*r*v/100*scale,cy+math.sin(-math.pi/2+2*math.pi*i/24)*r*v/100*scale) for i,v in enumerate(m['lqa'])]
   line(im,pts+[pts[0]],COLORS[j],4)
  txt(im,(1040,315),'24-language mean',28,MUTED)
  for j,m in enumerate(selected):
   yy=380+j*123;box(im,(1020,yy-8,1826,yy+94),'white',15)
   line(im,[(1043,yy+36),(1100,yy+36)],COLORS[j],7);txt(im,(1124,yy+8),m['model'],33,COLORS[j],True);txt(im,(1650,yy+5),f"{m['lqa_mean']:.1f}%",40,COLORS[j],True)
  txt(im,(1040,902),'Four selected models from the paper.',28,MUTED)
  txt(im,(1040,945),'Means use published, rounded scores.',25,MUTED)
 elif n==5:
  header(im,'One benchmark. Two ways to ask.')
  box(im,(76,258,1844,412));txt(im,(110,282),'LQA',42,TEAL,True,True);txt(im,(350,290),'Visual = question = answer language',40);txt(im,(1490,302),'24 settings',32,MUTED)
  box(im,(76,436,1844,590));txt(im,(110,460),'XQA',42,NAVY,True,True);txt(im,(350,468),'Fixed English or Chinese QA; change the visual',37);txt(im,(1490,536),'23 + 23 settings',27,MUTED)
  for x,big,small in [(80,'128','seed questions'),(530,'24','languages'),(980,'8,960','QA configurations'),(1490,'25','evaluated models')]:
   txt(im,(x,658),big,80,NAVY,True,True);txt(im,(x,762),small,31,MUTED)
  txt(im,(80,876),'Explore the data. Compare language robustness.',42,TEAL,True)
  txt(im,(80,946),'arnodjiang.github.io/MInfoVisQA',31,NAVY)
 return im
if __name__ == '__main__':
 # Static poster uses the real paired example with sufficient reading time.
 scene(2,4).save(OUT/'poster.jpg',quality=94)
 cmd=['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'minfovisqa-demo.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open('/tmp/minfovis-demo-ffmpeg.log','w'))
 for n,dur in enumerate(DUR):
  print(f'Rendering scene {n+1}/6',flush=True)
  static={}
  for frame in range(dur*FPS):
   t=frame/FPS
   # Cache static compositions; only transitions and radar build vary.
   state=int(t>=2)+2*int(t>=4) if n==1 else (min(3,int(t/2.25)) if n==3 else (round(t,3) if t<1.5 else 1000) if n==4 else 0)
   if state not in static:static[state]=scene(n,t)
   im=static[state].copy()
   if t<.35 and n>0:im=Image.blend(scene(n-1,DUR[n-1]-.01),im,t/.35)
   ImageDraw.Draw(im).rectangle((0,H-5,int(W*(START[n]+t)/sum(DUR)),H),fill=TEAL)
   p.stdin.write(im.tobytes())
  scene(n,dur-1).resize((960,540)).save(OUT/f'scene-{n+1}.jpg',quality=90)
 p.stdin.close();assert p.wait()==0
 # Compact looping README preview: paired example plus a real language switch.
 subprocess.run(['ffmpeg','-y','-ss','5','-t','16','-i',str(OUT/'minfovisqa-demo.mp4'),'-filter_complex','fps=4,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer','-loop','0',str(OUT/'preview.gif')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 print('Finished',flush=True)
