"""Build four static face directions, preserving approved bodies and hair outside facial features.
New C/D art comes from ImageGen; only sampling and compositing occur here.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
REGIONS=[(72,53,80,61),(82,53,87,60),(77,61,85,66)]
def detail(source,index):
    W,H=source.size
    assert (W,H)==(1254,1254)
    cell=source.crop(((index%2)*627,(index//2)*627,(index%2+1)*627,(index//2+1)*627)).convert("RGBA")
    translations=json.loads((ROOT/"idle-registration.json").read_text())["frames"]
    shifted=Image.new("RGBA",(627,627));shifted.alpha_composite(cell,tuple(translations[index]["translation"]))
    raw=np.asarray(shifted)
    colors=np.array([tuple(bytes.fromhex(c["hex"][1:])) for c in json.loads((ROOT/"idle-finished/palette.json").read_text())["colors"]],dtype=float)
    ref=json.loads((ROOT/"idle-finished/finish.json").read_text())
    s=ref["scale"];ax,ay=ref["anchorSource"];tx,ty=ref["anchor"]
    result=np.asarray(Image.open(ROOT/"idle-finished/frames/frame-00.png").convert("RGBA")).copy()
    for l,t,r,b in REGIONS:
        for y in range(t,b):
            for x in range(l,r):
                x0=int(np.floor(ax+(x-tx)/s));x1=int(np.ceil(ax+(x+1-tx)/s))
                y0=int(np.floor(ay+(y-ty)/s));y1=int(np.ceil(ay+(y+1-ty)/s))
                px=raw[y0:y1,x0:x1,:3].reshape(-1,3).astype(float)
                # Never mix the magenta key into facial edge colours.
                is_key=(px[:,0]>170)&(px[:,1]<100)&(px[:,2]>140)
                px=px[~is_key]
                if len(px)==0:
                    continue
                ink=(px@np.array([.2126,.7152,.0722]))<90
                color=px[ink].mean(axis=0) if ink.mean()>=.20 else px.mean(axis=0)
                result[y,x,:3]=colors[((colors-color)**2).sum(axis=1).argmin()].astype(np.uint8)
    return result
def blue_variant(a):
    b=a.copy();yy,xx=np.indices(a.shape[:2]);region=(yy>=68)&(yy<100)&(xx>=58)&(xx<89)&(a[:,:,3]==255)
    for old,new in [((84,68,31),(36,43,52)),((110,90,41),(50,61,72)),((124,104,48),(71,83,91)),((139,116,55),(97,110,114))]:
        mask=region&np.all(a[:,:,:3]==old,axis=2);b[mask,:3]=new
    return b
def main():
    (OUT/"combinations").mkdir(exist_ok=True)
    source=Image.open(OUT/"source.png")
    c=detail(source,0);d=detail(source,2)
    Image.fromarray(c).save(OUT/"face-c-detail.png");Image.fromarray(d).save(OUT/"face-d-detail.png")
    b=np.asarray(Image.open(ROOT/"face-b-v2/face-detail.png").convert("RGBA"))
    mask=np.zeros((160,128),dtype=bool)
    for l,t,r,bottom in REGIONS:mask[t:bottom,l:r]=True
    styles=[("ha","原始髮型"),("hb","短偏分"),("hc","微蓬後梳"),("hd","微捲短髮"),("he","低束小髮髻")]
    faces=[("fa","A 安靜",None),("fb","B 溫和",b),("fc","C 好奇",c),("fd","D 倔強",d)]
    font=ImageFont.truetype("C:/Windows/Fonts/msjh.ttc",22)
    small=ImageFont.truetype("C:/Windows/Fonts/msjh.ttc",16)
    allheads=Image.new("RGB",(260*5,270*4),"#eee7da");draw_all=ImageDraw.Draw(allheads)
    lineup=Image.new("RGB",(384*4,530),"#eee7da");draw=ImageDraw.Draw(lineup)
    headrow=Image.new("RGB",(320*4,330),"#eee7da");draw_head=ImageDraw.Draw(headrow)
    counts=[]
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/"combinations").glob("*.png")}
    for col,(style,title) in enumerate(styles):
        base=np.asarray(Image.open(ROOT/"combinations"/f"{style}-fa-oa.png").convert("RGBA")).copy()
        rendered=[]
        for row,(faceid,label,patch) in enumerate(faces):
            a=base.copy()
            if patch is not None:
                visible=mask&(a[:,:,3]>127)&(patch[:,:,3]>127)
                a[visible,:3]=patch[visible,:3]
            assert np.array_equal(a[~mask],base[~mask])
            assert np.array_equal(a[:,:,3],base[:,:,3])
            for outfit,arr in [("oa",a),("ob",blue_variant(a))]:
                Image.fromarray(arr).save(OUT/"combinations"/f"{style}-{faceid}-{outfit}.png")
            image=Image.fromarray(a)
            crop=image.crop((52,34,96,69)).resize((220,175),Image.Resampling.NEAREST)
            allheads.paste(crop,(col*260+20,row*270+30),crop)
            draw_all.text((col*260+20,row*270+220),label+" / "+title,font=small,fill="#443d35")
            if style=="hb":
                zoom=image.resize((384,480),Image.Resampling.NEAREST)
                lineup.paste(zoom,(row*384,0),zoom)
                draw.text((row*384+80,488),label,font=font,fill="#443d35")
                large=image.crop((52,34,96,69)).resize((264,210),Image.Resampling.NEAREST)
                headrow.paste(large,(row*320+28,20),large)
                draw_head.text((row*320+80,265),label,font=font,fill="#443d35")
            rendered.append(a)
        assert len({a.tobytes() for a in rendered})==4
        counts.append({"hair":style,"changed_pixels_vs_a":[int(np.any(x!=base,axis=2).sum()) for x in rendered]})
    for name,sha in before.items():assert hashlib.sha256((ROOT/"combinations"/name).read_bytes()).hexdigest()==sha
    lineup.save(OUT/"comparison.png");lineup.save(ROOT/"faces-review.png")
    headrow.save(OUT/"faces-closeup.png")
    allheads.save(OUT/"all-hairstyles.png")
    qa={"status":"needs-visual-review","directions":["quiet","warm smiling eyes","curious","stubborn"],
      "same_canvas":[128,160],"same_palette":True,"same_scale":True,
      "unchanged_outside_feature_regions":True,"unchanged_silhouette":True,
      "all_four_unique_each_hairstyle":True,"approved_active_images_unchanged":True,
      "proposal_images":len(list((OUT/"combinations").glob("*.png"))),"counts":counts,
      "limits":["C/D static art awaits user review","no universal face layers for all directions",
      "no generated-frame animation used","one clothing design with two palette variants"]}
    assert qa["proposal_images"]==40
    (OUT/"qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    print(json.dumps(qa))
if __name__=="__main__":main()

