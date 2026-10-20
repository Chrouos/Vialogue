"""Finish generated hair/jacket refinements over existing static combinations."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_propagation,label
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
HAIRS=[('ha','原始髮型'),('hb','短偏分'),('hc','俐落後梳'),('hd','蓬鬆微捲'),('he','低束小髮髻')]
OUTFITS=[('tshirt-jeans','T-shirt＋牛仔褲'),('cardigan-straight','針織外套＋直筒褲'),('jacket-shorts','輕薄短外套＋短褲')]

def reduce_rgba(rgb,opaque,size):
    alpha=np.asarray(Image.fromarray(opaque.astype('float32')).resize(size,Image.Resampling.BOX))
    result=np.zeros((size[1],size[0],4),np.uint8)
    for c in range(3):
        prem=np.asarray(Image.fromarray((rgb[:,:,c]*opaque).astype('float32')).resize(size,Image.Resampling.BOX))
        result[:,:,c]=np.clip(prem/np.maximum(alpha,1e-6),0,255).astype(np.uint8)
    result[:,:,3]=(alpha>=.5)*255
    return result

def nearest(a,colors):
    result=a.copy();pixels=a[a[:,:,3]>0,:3].astype(float)
    result[a[:,:,3]>0,:3]=colors[((pixels[:,None,:]-colors[None,:,:])**2).sum(axis=2).argmin(axis=1)].astype(np.uint8)
    result[a[:,:,3]==0,:3]=0
    return result

def main():
    (OUT/'frames').mkdir(exist_ok=True);(OUT/'heads').mkdir(exist_ok=True)
    oldroot=ROOT/'outfit-hair-validation-v1/frames'
    oldpaths=list(oldroot.glob('*.png'))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in oldpaths}
    palette=np.array([tuple(bytes.fromhex(c['hex'][1:])) for c in json.loads((ROOT/'idle-finished/palette.json').read_text())['colors']],float)
    hairsource=Image.open(OUT/'hair-source.png').convert('RGB')
    assert hairsource.size==(1536,1024)
    heads=[]
    for i,(hair,name) in enumerate(HAIRS):
        rgb=np.asarray(hairsource.crop(((i%3)*512+124,(i//3)*512+120,(i%3)*512+388,(i//3)*512+330))).astype(float)
        bg=np.median(rgb[:8,:8],axis=(0,1))
        candidate=np.linalg.norm(rgb-bg,axis=2)<36
        seed=np.zeros(candidate.shape,bool);seed[[0,-1],:]=True;seed[:,[0,-1]]=True
        transparent=binary_propagation(seed&candidate,mask=candidate)
        patch=nearest(reduce_rgba(rgb,~transparent,(44,35)),palette)
        old=np.asarray(Image.open(oldroot/f'{hair}-tshirt-jeans.png').convert('RGBA'))
        a=np.zeros_like(old);a[34:69,52:96]=patch
        # Preserve current neutral pupils, mouth and lower face; edit hair/eye gap.
        a[60:65]=old[60:65]
        a[56:59,73:77]=old[56:59,73:77]
        a[55:59,83:85]=old[55:59,83:85]
        a[65:]=0
        Image.fromarray(a).save(OUT/'heads'/f'{hair}.png');heads.append(a)
    jacket=Image.open(OUT/'jacket-source.png').convert('RGB');assert jacket.size==(1536,1024)
    rgb=np.asarray(jacket.crop((1024,192,1536,832))).astype(float)
    key=(rgb[:,:,0]>170)&(rgb[:,:,1]<115)&(rgb[:,:,2]>145)
    body=reduce_rgba(rgb,~key,(128,160))
    oldjacket=np.asarray(Image.open(ROOT/'modern-outfits-v2/frames/jacket-shorts.png').convert('RGBA')).copy()
    body[:65]=oldjacket[:65];body[99:]=oldjacket[99:]
    samples=body[65:99,:,:3][body[65:99,:,3]>0]
    q=Image.fromarray(samples.reshape(1,-1,3)).quantize(colors=24,dither=Image.Dither.NONE)
    cols=np.array(q.getpalette()[:72],np.uint8).reshape(-1,3).astype(float)
    torso=nearest(body,cols);body[65:99]=torso[65:99]
    Image.fromarray(body).save(OUT/'light-jacket.png')
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',18)
    small=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',14)
    overview=Image.new('RGB',(1280,1160),'#eee7da');d=ImageDraw.Draw(overview)
    native=Image.new('RGB',(800,680),'#eee7da');dn=ImageDraw.Draw(native)
    haircompare=Image.new('RGB',(1600,640),'#eee7da');dh=ImageDraw.Draw(haircompare)
    records=[]
    for col,((hair,name),head) in enumerate(zip(HAIRS,heads)):
        oldhead=Image.open(oldroot/f'{hair}-tshirt-jeans.png').convert('RGBA')
        after=np.asarray(oldhead).copy();after[:65]=head[:65]
        for row,img in enumerate([oldhead,Image.fromarray(after)]):
            crop=img.crop((52,34,96,69)).resize((264,210),Image.Resampling.NEAREST)
            haircompare.paste(crop,(col*320+28,row*320+15),crop)
            dh.text((col*320+50,row*320+250),('調整前 / ' if row==0 else '調整後 / ')+name,font=font,fill='#443d35')
        for row,(oid,title) in enumerate(OUTFITS):
            base=np.asarray(Image.open(ROOT/'modern-outfits-v2/frames'/f'{oid}.png').convert('RGBA')).copy()
            a=body.copy() if oid=='jacket-shorts' else base.copy()
            a[:65]=head[:65]
            assert np.array_equal(a[:65],head[:65])
            if oid!='jacket-shorts':assert np.array_equal(a[65:],base[65:])
            else:assert np.array_equal(a[99:],base[99:])
            assert np.array_equal(a[61:64,77:83],oldhead.crop((77,61,83,64)))
            assert set(np.unique(a[:,:,3])).issubset({0,255})
            cc,_=label(a[:,:,3]>0);assert cc[57,78]>0 and cc[57,78]==cc[80,74]
            yy,xx=np.where(a[:,:,3]>0);assert yy.max()==147
            img=Image.fromarray(a);img.save(OUT/'frames'/f'{hair}-{oid}.png')
            zoom=img.resize((256,320),Image.Resampling.NEAREST)
            overview.paste(zoom,(col*256,row*380+20),zoom)
            d.text((col*256+70,row*380+340),name,font=font,fill='#443d35');d.text((col*256+40,row*380+365),title,font=small,fill='#443d35')
            native.paste(img,(col*160+16,row*220+10),img)
            dn.text((col*160+35,row*220+177),name,font=small,fill='#443d35');dn.text((col*160+5,row*220+200),title,font=small,fill='#443d35')
            records.append({'hair':hair,'outfit':oid,'file':f'frames/{hair}-{oid}.png','feet_y':147})
    assert all(hashlib.sha256((oldroot/name).read_bytes()).hexdigest()==sha for name,sha in hashes.items())
    overview.save(OUT/'combinations-review.png');native.save(OUT/'native-size.png');haircompare.save(OUT/'hair-before-after.png')
    qa={'art_source':'host_image + existing','status':'needs-user-visual-review','images':15,'canvas':[128,160],'old_files_unchanged':True,'neutral_mouth_and_pupil_cores_preserved':True,'first_two_outfit_bodies_unchanged':True,'third_shorts_legs_shoes_unchanged':True,'feet_y':147,'head_torso_connected':True,'records':records,'limits':['refined hairstyles and jacket are proposals, not automatically approved','only neutral static three-quarter pose','hair colors are planned only, current art stays coffee brown','other expressions and motions not verified']}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in qa.items() if k!='records'},ensure_ascii=False))
if __name__=='__main__':main()
