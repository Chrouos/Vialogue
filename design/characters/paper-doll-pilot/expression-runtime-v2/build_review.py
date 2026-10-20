"""Composite ImageGen's small-face edit onto the approved fixed body."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
LABELS=['一般','開心','超開心','為難','傷心','超傷心','害羞','生氣']
REGIONS=[(74,52,85,55),(72,55,87,61),(72,61,87,66)]

def main():
    src=Image.open(OUT/'source.png').convert('RGB')
    basepath=ROOT/'combinations/hb-fa-oa.png'
    base=np.asarray(Image.open(basepath).convert('RGBA')).copy()
    original=hashlib.sha256(basepath.read_bytes()).hexdigest()
    pal=np.array([tuple(bytes.fromhex(c['hex'][1:])) for c in json.loads((ROOT/'idle-finished/palette.json').read_text())['colors']]+[(218,139,116),(244,178,146),(91,163,190),(168,222,232)],dtype=float)
    mask=np.zeros((160,128),bool)
    for l,t,r,b in REGIONS:mask[t:b,l:r]=True
    (OUT/'frames').mkdir(exist_ok=True)
    native=Image.new('RGB',(640,410),'#eee7da');dn=ImageDraw.Draw(native)
    full=Image.new('RGB',(1024,720),'#eee7da');df=ImageDraw.Draw(full)
    heads=Image.new('RGB',(1120,580),'#eee7da');dh=ImageDraw.Draw(heads)
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',18)
    cw=src.width/4;ch=src.height/2
    counts=[];rendered=[]
    for i,label in enumerate(LABELS):
        cell=src.crop((round(i%4*cw),round(i//4*ch),round((i%4+1)*cw),round((i//4+1)*ch)))
        raw=np.asarray(cell);h,w=raw.shape[:2];a=base.copy()
        for y,x in zip(*np.where(mask)):
            if i not in (4,5):continue
            if not base[y,x,3]:continue
            px=raw[int(y*h/160):max(int((y+1)*h/160),int(y*h/160)+1),int(x*w/128):max(int((x+1)*w/128),int(x*w/128)+1)].reshape(-1,3).astype(float)
            px=px[~((px[:,0]>170)&(px[:,1]<100)&(px[:,2]>140))]
            if not len(px):continue
            ink=(px@np.array([.2126,.7152,.0722]))<95
            # Retain narrow generated marks without averaging them into skin.
            blue=(px[:,2]>px[:,0]+12)&(px[:,1]>px[:,0]+8)&(px[:,2]>120)
            if i==5 and blue.mean()>=.20:
                color=np.median(px[blue],axis=0)
            elif ink.mean()>=.24:
                color=np.median(px[ink],axis=0)
            else:
                skin=px[~ink]
                color=np.median(skin if len(skin) else px,axis=0)
            a[y,x,:3]=pal[((pal-color)**2).sum(axis=1).argmin()].astype(np.uint8)
        if i not in (4,5):
            a=np.asarray(Image.open(ROOT/'expression-runtime-v1/frames'/f'{i:02}.png').convert('RGBA')).copy()
        assert np.array_equal(a[~mask],base[~mask])
        assert np.array_equal(a[:,:,3],base[:,:,3])
        image=Image.fromarray(a);image.save(OUT/'frames'/f'{i:02}.png');rendered.append(a)
        if i not in (4,5):
            assert (OUT/'frames'/f'{i:02}.png').read_bytes()==(ROOT/'expression-runtime-v1/frames'/f'{i:02}.png').read_bytes()
        col=i%4;row=i//4
        native.paste(image,(col*160+16,row*205),image);dn.text((col*160+48,row*205+172),label,font=font,fill='#443d35')
        zoom=image.resize((256,320),Image.Resampling.NEAREST);full.paste(zoom,(col*256,row*360),zoom);df.text((col*256+90,row*360+329),label,font=font,fill='#443d35')
        crop=image.crop((52,34,96,69)).resize((264,210),Image.Resampling.NEAREST);heads.paste(crop,(col*280+8,row*290+10),crop);dh.text((col*280+95,row*290+244),label,font=font,fill='#443d35')
        counts.append(int(np.any(a!=base,axis=2).sum()))
    native.save(OUT/'native-size.png');full.save(OUT/'full-body.png');heads.save(OUT/'faces-closeup.png')
    assert hashlib.sha256(basepath.read_bytes()).hexdigest()==original
    assert len({a.tobytes() for a in rendered})==8
    tears=int(((rendered[5][:,:,2].astype(int)>rendered[5][:,:,0].astype(int)+12)&(rendered[5][:,:,1].astype(int)>rendered[5][:,:,0].astype(int)+8)&mask).sum())
    qa={'art_source':'host_image','status':'needs-user-visual-review','canvas':[128,160],'hair':'approved hb short side part','palette':'approved 30 colors plus 2 blush and 2 tear colors','all_eight_unique':True,'unchanged_outside_feature_regions':True,'unchanged_alpha':True,'base_unchanged':True,'six_other_emotions_byte_identical_to_v1':True,'cyan_tear_pixels':tears,'base_sha256':original,'changed_pixels':counts,'feature_regions':REGIONS,'limits':['static trial for one hair only','not universal modular face layers','no animation integration','sadness revision awaits visual approval']}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(qa))
if __name__=='__main__':main()
