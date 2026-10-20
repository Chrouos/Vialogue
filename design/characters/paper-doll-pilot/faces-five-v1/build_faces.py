"""Transfer generated expression details onto approved static sprites; no art drawing."""
from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
spec=importlib.util.spec_from_file_location('previous',ROOT/'faces-four-v1/build_faces.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
REGIONS=previous.REGIONS
FACES=[('fdash','-.-'),('fhappy','^_^'),('fquiet','無口'),('fsad','憂鬱'),('fgentle','溫柔')]
HAIR=[('ha','原始髮型'),('hb','短偏分'),('hc','微蓬後梳'),('hd','微捲短髮'),('he','低束小髮髻')]

def sample(source,index):
    cell=source.width//3
    raw=np.asarray(source.crop(((index%3)*cell,(index//3)*cell,(index%3+1)*cell,(index//3+1)*cell)).convert('RGB'))
    colors=np.array([tuple(bytes.fromhex(c['hex'][1:])) for c in json.loads((ROOT/'idle-finished/palette.json').read_text())['colors']],dtype=float)
    ref=json.loads((ROOT/'idle-finished/finish.json').read_text());s=ref['scale'];ax,ay=ref['anchorSource'];tx,ty=ref['anchor']
    ratio=cell/627
    result=np.asarray(Image.open(ROOT/'idle-finished/frames/frame-00.png').convert('RGBA')).copy()
    for l,t,r,b in REGIONS:
        for y in range(t,b):
            for x in range(l,r):
                x0=int(np.floor((ax+(x-tx)/s)*ratio));x1=int(np.ceil((ax+(x+1-tx)/s)*ratio))
                y0=int(np.floor((ay+(y-ty)/s)*ratio));y1=int(np.ceil((ay+(y+1-ty)/s)*ratio))
                px=raw[y0:y1,x0:x1].reshape(-1,3).astype(float)
                px=px[~((px[:,0]>170)&(px[:,1]<100)&(px[:,2]>140))]
                if not len(px):continue
                ink=px@np.array([.2126,.7152,.0722])<90
                color=px[ink].mean(axis=0) if ink.mean()>=.20 else px.mean(axis=0)
                result[y,x,:3]=colors[((colors-color)**2).sum(axis=1).argmin()].astype(np.uint8)
    return result

def main():
    (OUT/'combinations').mkdir(exist_ok=True)
    source=Image.open(OUT/'source.png');assert source.size==(1536,1024)
    patches=[sample(source,i) for i in range(5)]
    mask=np.zeros((160,128),bool)
    for l,t,r,b in REGIONS:mask[t:b,l:r]=True
    before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'combinations').glob('*.png')}
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',22)
    small=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',16)
    lineup=Image.new('RGB',(1920,530),'#eee7da');dl=ImageDraw.Draw(lineup)
    heads=Image.new('RGB',(1600,330),'#eee7da');dh=ImageDraw.Draw(heads)
    allheads=Image.new('RGB',(1300,1350),'#eee7da');da=ImageDraw.Draw(allheads)
    native=Image.new('RGB',(640,195),'#eee7da');dn=ImageDraw.Draw(native)
    for col,(hair,title) in enumerate(HAIR):
        base=np.asarray(Image.open(ROOT/'combinations'/f'{hair}-fa-oa.png').convert('RGBA')).copy()
        rendered=[]
        for row,((face,label),patch) in enumerate(zip(FACES,patches)):
            a=base.copy();visible=mask&(a[:,:,3]>127)&(patch[:,:,3]>127)
            a[visible,:3]=patch[visible,:3]
            assert np.array_equal(a[~mask],base[~mask])
            assert np.array_equal(a[:,:,3],base[:,:,3])
            rendered.append(a)
            for outfit,arr in [('oa',a),('ob',previous.blue_variant(a))]:Image.fromarray(arr).save(OUT/'combinations'/f'{hair}-{face}-{outfit}.png')
            img=Image.fromarray(a)
            crop=img.crop((52,34,96,69)).resize((220,175),Image.Resampling.NEAREST)
            allheads.paste(crop,(col*260+20,row*270+30),crop)
            da.text((col*260+20,row*270+220),label+' / '+title,font=small,fill='#443d35')
            if hair=='hb':
                zoom=img.resize((384,480),Image.Resampling.NEAREST);lineup.paste(zoom,(row*384,0),zoom)
                dl.text((row*384+100,488),label,font=font,fill='#443d35')
                crop=img.crop((52,34,96,69)).resize((264,210),Image.Resampling.NEAREST);heads.paste(crop,(row*320+28,20),crop)
                dh.text((row*320+100,265),label,font=font,fill='#443d35')
                native.paste(img,(row*128,0),img);dn.text((row*128+30,165),label,font=small,fill='#443d35')
        assert len({a.tobytes() for a in rendered})==5
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha for p,sha in before.items())
    for filename,img in [('comparison.png',lineup),('faces-closeup.png',heads),('all-hairstyles.png',allheads),('native-size.png',native)]:img.save(OUT/filename)
    lineup.save(ROOT/'faces-review.png')
    qa={'status':'needs-user-visual-review','expressions':[v for k,v in FACES],'proposal_images':len(list((OUT/'combinations').glob('*.png'))),'canvas':[128,160],'all_five_unique_each_hair':True,'unchanged_outside_feature_regions':True,'unchanged_alpha':True,'approved_active_images_unchanged':True,'animation':'not generated; static proposals only'}
    assert qa['proposal_images']==50
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(qa,ensure_ascii=False))
if __name__=='__main__':main()
