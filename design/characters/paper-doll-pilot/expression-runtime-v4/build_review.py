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
    src=Image.open(OUT/'source-heads.png').convert('RGB')
    basepath=ROOT/'combinations/hb-fa-oa.png'
    base=np.asarray(Image.open(basepath).convert('RGBA')).copy()
    original=hashlib.sha256(basepath.read_bytes()).hexdigest()
    pal=np.array([tuple(bytes.fromhex(c['hex'][1:])) for c in json.loads((ROOT/'idle-finished/palette.json').read_text())['colors']]+[(218,139,116),(244,178,146),(91,163,190),(168,222,232),(216,105,108),(178,77,83)],dtype=float)
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
        # Head-edit guide uses an enlarged 44x35 crop at (60,120) in each cell.
        cell=cell.resize((384,512),Image.Resampling.BOX)
        head=cell.crop((60,120,324,330)).resize((44,35),Image.Resampling.BOX)
        cell=Image.new('RGB',(128,160),'#ff00ff');cell.paste(head,(52,34))
        raw=np.asarray(cell);h,w=raw.shape[:2];a=base.copy()
        for y,x in zip(*np.where(mask)):
            if i in (0,2):continue
            # Chin/neck shade is not a mouth feature; retain the approved pixels.
            if y>=64:continue
            if not base[y,x,3]:continue
            px=raw[int(y*h/160):max(int((y+1)*h/160),int(y*h/160)+1),int(x*w/128):max(int((x+1)*w/128),int(x*w/128)+1)].reshape(-1,3).astype(float)
            px=px[~((px[:,0]>170)&(px[:,1]<100)&(px[:,2]>140))]
            if not len(px):continue
            ink=(px@np.array([.2126,.7152,.0722]))<120
            # Retain narrow generated marks without averaging them into skin.
            blue=(px[:,2]>px[:,0]+12)&(px[:,1]>px[:,0]+8)&(px[:,2]>120)
            rose=(px[:,0]>150)&(px[:,1]<px[:,0]*.72)&(px[:,2]>px[:,1]*.65)&(px[:,2]>75)
            if i==6 and y>=59 and rose.mean()>=.20:
                color=np.median(px[rose],axis=0)
            elif i==5 and blue.mean()>=.20:
                color=np.median(px[blue],axis=0)
            elif ink.mean()>=.24:
                color=np.median(px[ink],axis=0)
            else:
                skin=px[~ink]
                color=np.median(skin if len(skin) else px,axis=0)
            a[y,x,:3]=pal[((pal-color)**2).sum(axis=1).argmin()].astype(np.uint8)
        if i==3:
            old=np.asarray(Image.open(ROOT/'expression-runtime-v3/frames/03.png').convert('RGBA'))
            a[52:55,74:85]=old[52:55,74:85]
        if i in (1,3,4,5,6):
            # Isolate the generated lip pigment from golden skin, then compress
            # that existing glyph vertically; do not treat chin shade as lips.
            lips=raw[61:64,77:82,:3].astype(float)
            lum=lips@np.array([.2126,.7152,.0722])
            pigment=(lum<185)&(lips[:,:,0]-lips[:,:,1]>30)
            if pigment.any():
                yy,xx=np.where(pigment)
                glyph=Image.fromarray((pigment[yy.min():yy.max()+1,xx.min():xx.max()+1]*255).astype(np.uint8))
                width=3 if i==1 else 2
                height=2 if i==1 else 1
                reduced=np.asarray(glyph.resize((width,height),Image.Resampling.BOX))>90
                a[61:64,77:82,:3]=(250,208,147)
                start=79-width//2
                for dy in range(height):
                    for dx in range(width):
                        if reduced[dy,dx]:a[62-height+1+dy,start+dx,:3]=(119,71,43)
        if i in (0,2):
            a=np.asarray(Image.open(ROOT/'expression-runtime-v2/frames'/f'{i:02}.png').convert('RGBA')).copy()
        assert np.array_equal(a[~mask],base[~mask])
        assert np.array_equal(a[:,:,3],base[:,:,3])
        image=Image.fromarray(a);image.save(OUT/'frames'/f'{i:02}.png');rendered.append(a)
        if i in (0,2):
            assert (OUT/'frames'/f'{i:02}.png').read_bytes()==(ROOT/'expression-runtime-v2/frames'/f'{i:02}.png').read_bytes()
        col=i%4;row=i//4
        native.paste(image,(col*160+16,row*205),image);dn.text((col*160+48,row*205+172),label,font=font,fill='#443d35')
        zoom=image.resize((256,320),Image.Resampling.NEAREST);full.paste(zoom,(col*256,row*360),zoom);df.text((col*256+90,row*360+329),label,font=font,fill='#443d35')
        crop=image.crop((52,34,96,69)).resize((264,210),Image.Resampling.NEAREST);heads.paste(crop,(col*280+8,row*290+10),crop);dh.text((col*280+95,row*290+244),label,font=font,fill='#443d35')
        counts.append(int(np.any(a!=base,axis=2).sum()))
    native.save(OUT/'native-size.png');full.save(OUT/'full-body.png');heads.save(OUT/'faces-closeup.png')
    assert hashlib.sha256(basepath.read_bytes()).hexdigest()==original
    assert len({a.tobytes() for a in rendered})==8
    tears=int(((rendered[5][:,:,2].astype(int)>rendered[5][:,:,0].astype(int)+12)&(rendered[5][:,:,1].astype(int)>rendered[5][:,:,0].astype(int)+8)&mask).sum())
    blush=int((np.all(rendered[6][:,:,:3]==(216,105,108),axis=2)|np.all(rendered[6][:,:,:3]==(178,77,83),axis=2)).sum())
    qa={'art_source':'host_image','status':'needs-user-visual-review','canvas':[128,160],'hair':'approved hb short side part','palette':'approved30 + 4 blush + 2 tear colors','all_eight_unique':True,'unchanged_outside_feature_regions':True,'unchanged_alpha':True,'base_unchanged':True,'neutral_and_very_happy_byte_identical_to_v2':True,'awkward_brow_preserved_from_v3':True,'chin_shading_not_reclassified_as_mouth':True,'cyan_tear_pixels':tears,'strong_rose_pixels':blush,'base_sha256':original,'changed_pixels':counts,'feature_regions':REGIONS,'limits':['static trial for one hair only','not universal modular face layers','no animation integration','mouth and sampling revision awaits visual approval']}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(qa))
if __name__=='__main__':main()
