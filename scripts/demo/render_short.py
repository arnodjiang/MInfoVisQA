"""Render the 25-second homepage film from released images (Pillow and FFmpeg)."""
from functools import lru_cache
from pathlib import Path
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "site/assets"
OUT = ASSETS / "demo"
W, H = 1600, 900
FPS = 24
INK, PAPER = "#102A36", "#F8F6EC"
MINT, GOLD = "#9FE5D2", "#FFD38B"
STEEL = "#AEC6CE"
SCENES = [(0, "cover"), (4.5, "en"), (8, "ja"), (11.5, "chart"), (15, "table"), (18.5, "end")]


@lru_cache(None)
def font(size, face="sans"):
    apple = {"sans": "Arial.ttf", "bold": "Arial Bold.ttf", "serif": "Georgia.ttf",
             "italic": "Georgia Italic.ttf", "mono": "Courier New Bold.ttf"}
    free = {"sans": "DejaVuSans.ttf", "bold": "DejaVuSans-Bold.ttf",
            "serif": "DejaVuSerif.ttf", "italic": "DejaVuSerif-Italic.ttf",
            "mono": "DejaVuSansMono.ttf"}
    path = Path("/System/Library/Fonts/Supplemental") / apple[face]
    return ImageFont.truetype(str(path) if path.exists() else free[face], size)


def label(d, x, y, value, size, color=INK, face="sans", anchor="lt"):
    d.text((x, y), value, font=font(size, face), fill=color, anchor=anchor)


def brand(d, dark=False):
    color = PAPER if dark else INK
    for i, h in enumerate((13, 23, 34)):
        d.rounded_rectangle((72+i*12, 87-h, 80+i*12, 87), 2, fill=MINT if dark else "#177668")
    label(d, 121, 53, "MInfoVisQA", 41, color, "bold")


def footer(d, left, right, dark=False):
    color = STEEL if dark else "#47656B"
    d.line((72,803,1528,803),fill="#3B5661" if dark else "#B2C4C2",width=2)
    label(d,72,830,left,26,color)
    label(d,1528,830,right,25,color,"sans","rt")


def cover(records):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 257), fill=INK)
    brand(d, True)
    label(d, 1528, 64, "24 languages   /   8,960 QA configurations", 27, STEEL, "sans", "rt")
    label(d, 68, 118, "Same question.", 83, PAPER, "serif")
    label(d, 678, 118, "Different answers.", 83, MINT, "italic")
    prompt = records[0]["question"].splitlines()[0]
    label(d, 72, 219, prompt, 29, PAPER)
    d.line((800, 294, 800, 794), fill="#D0DBD9", width=2)
    for i, (lang, name, accent) in enumerate((("en", "English", "#146553"), ("ja", "Japanese", "#954718"))):
        record = next(r for r in records if r["language"] == lang)
        x = 72 + i * 755
        label(d, x, 288, name + " chart", 39, INK, "bold")
        label(d, x + 694, 297, "ChartQAPro", 24, "#506569", "sans", "rt")
        # Identical crops preserve scale and alignment while removing the repeated
        # chart title, source credit and white margin from the thumbnail.
        with Image.open(OUT / f"case-{lang}.png") as src:
            chart = src.convert("RGB").crop((10, 203, 1090, 730))
        im.paste(chart.resize((688, 336), Image.Resampling.LANCZOS), (x, 349))
        d.line((x, 701, x + 694, 701), fill="#B5C7C4", width=2)
        label(d, x, 727, record["prediction"], 68, accent, "serif")
        tag = "Correct" if record["correct"] else "Incorrect"
        label(d, x + 694, 753, tag, 30, accent, "bold", "rt")
    d.rectangle((0, 820, W, H), fill="#EAF1EF")
    label(d, 72, 846, "Recorded answers  /  GPT-5.6-Luna", 30, INK)
    label(d, 1528, 846, "Reference answer: " + records[0]["reference"], 30, INK, "bold", "rt")
    return im


def place(im, source, rect):
    x,y,r,b=rect
    with Image.open(source) as orig:
        pic=orig.convert("RGB")
    pic=ImageOps.contain(pic,(r-x,b-y),Image.Resampling.LANCZOS)
    im.paste(pic,(x+(r-x-pic.width)//2,y+(b-y-pic.height)//2))


def evidence(record):
    en=record["language"]=="en"; language="English" if en else "Japanese"
    im=Image.new("RGB",(W,H),PAPER); d=ImageDraw.Draw(im); brand(d)
    label(d,1528,66,"ChartQAPro  /  GPT-5.6-Luna",26,INK,"sans","rt")
    d.rounded_rectangle((72,133,927,772),20,fill="white",outline="#D3DEDA",width=2)
    place(im,OUT/("case-"+record["language"]+".png"),(86,150,913,753))
    x=973
    label(d,x,170,"Question in English",28,"#416266","bold")
    for j,line in enumerate(("On average, which","season records the","highest number","of breakups?")):
        label(d,x,237+j*60,line,50,INK,"serif")
    d.rounded_rectangle((x,522,1528,720),19,fill=MINT if en else GOLD)
    label(d,x+30,552,"Model answer",27)
    label(d,x+26,605,record["prediction"],83,INK,"serif")
    footer(d,language+" chart","Reference answer: "+record["reference"])
    return im


def pair(kind):
    chart=kind=="chart"
    im=Image.new("RGB",(W,H),PAPER);d=ImageDraw.Draw(im);brand(d)
    label(d,1528,66,"ChartQA" if chart else "TableVQA-Bench",28,INK,"sans","rt")
    label(d,70,141,"One chart in two languages." if chart else "The same table, cell for cell.",76,INK,"serif")
    stem="6c1b80891d9f43724aa6" if chart else "345c918a890d9cdd8b8f"
    for j,lang in enumerate(("en","ja")):
        x=72+j*740
        d.rounded_rectangle((x,273,x+716,753),20,fill="white",outline="#CFDCD7",width=2)
        label(d,x+28,300,["English","Japanese"][j],32,INK,"bold")
        path=ASSETS/f"{stem}-{lang}.png"
        if chart:
            place(im,path,(x+12,346,x+704,736))
        else:
            with Image.open(path) as src:
                detail=src.convert("RGB").crop((35,35,1130,605))
            im.paste(detail.resize((676,352),Image.Resampling.LANCZOS),(x+20,363))
    footer(d,"Matched chart pair" if chart else "Matched table detail","24 visual languages")
    return im


def end():
    im=Image.new("RGB",(W,H),INK); d=ImageDraw.Draw(im);brand(d,True)
    label(d,72,177,"Multilingual visual",94,PAPER,"serif")
    label(d,72,285,"question answering.",94,MINT,"italic")
    for x,num,word in [(72,"128","seed questions"),(563,"24","visual languages"),(1055,"8,960","QA configurations")]:
        d.line((x,480,x+418,480),fill="#53707B",width=2)
        label(d,x,520,num,107,PAPER,"serif")
        label(d,x,654,word,34,STEEL)
    footer(d,"Explore the benchmark and leaderboard","arXiv 2611.21644",True)
    return im


def main():
    records=json.loads((OUT/"evidence.json").read_text())["records"]
    frames=[cover(records),*(evidence(next(r for r in records if r["language"]==lang)) for lang in ("en","ja")),
            pair("chart"),pair("table"),end()]
    frames[0].save(OUT/"poster.jpg",quality=94,subsampling=0)
    video=OUT/"minfovisqa-demo.mp4"
    # Feed static intervals as repeated raw frames. Dissolve only at chapter changes;
    # cut directly between paired charts so aligned features stay still.
    args=["ffmpeg","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24",
          "-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-an","-c:v","libx264",
          "-preset","fast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(video)]
    with subprocess.Popen(args,stdin=subprocess.PIPE) as stream:
        for i,(start,_) in enumerate(SCENES):
            duration=(SCENES[i+1][0] if i+1<len(SCENES) else 25)-start
            still=frames[i].tobytes()
            for n in range(round(duration*FPS)):
                if i in (1,3,5) and n<6:
                    stream.stdin.write(Image.blend(frames[i-1],frames[i],(n+1)/6).tobytes())
                else:
                    stream.stdin.write(still)
        stream.stdin.close()
        if stream.wait(): raise RuntimeError("FFmpeg encoding failed")
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",str(video),"-filter_complex",
                    "fps=4,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse",
                    "-loop","0",str(OUT/"preview.gif")],check=True)


if __name__=="__main__":
    main()
