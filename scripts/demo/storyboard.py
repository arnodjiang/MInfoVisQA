"""Capture editable text, shapes and source images from the video scene functions."""
import importlib.util,json
from pathlib import Path
p=Path(__file__).with_name('render.py');spec=importlib.util.spec_from_file_location('demo',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
slides=[];ops=[]
def text(im,xy,s,size=32,color=m.INK,bold=False,title=False):
 bb=m.font(size,bold,title).getbbox(s);ops.append(dict(type='text',x=xy[0],y=xy[1]+bb[1],w=bb[2]-bb[0]+16,h=size*1.4,text=s,size=size,color=color,bold=bold,title=title))
def box(im,rect,fill='white',r=24,outline=None):ops.append(dict(type='box',rect=rect,fill=fill))
def line(im,pts,c=m.TEAL,w=3):ops.append(dict(type='line',pts=pts,color=c,width=w))
def fit(im,path,rect):
 src=m.asset(path);x,y,w,h=rect;ratio=min(w/src.width,h/src.height);sw,sh=src.width*ratio,src.height*ratio
 ops.append(dict(type='image',path=str(Path(path).relative_to(m.ROOT)),rect=[x+(w-sw)/2,y+(h-sh)/2,sw,sh]))
m.txt=text;m.box=box;m.line=line;m.fit=fit
for n in range(6):
 ops=[];m.scene(n,m.DUR[n]-1)
 if n==4:ops=[o for o in ops if not ((o['type']=='text' and o['x']<950 and 260<o['y']<990) or (o['type']=='line' and o['pts'][0][0]<950 and o['pts'][0][1]>260))]
 slides.append(ops)
(m.ROOT/'build/demo/scenes.json').write_text(json.dumps(slides))
