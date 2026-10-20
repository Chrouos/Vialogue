"""Verify existing approved static assets by compositing hair deltas, no new art."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label as component_labels
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
HAIRS=[('ha','原始髮型'),('hb','短偏分'),('hc','微蓬後梳'),('hd','微捲短髮'),('he','低束小髮髻')]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=True);(OUT/'frames').mkdir(exist_ok=True)
    outfitroot=ROOT/'modern-outfits-v2'
    catalog=json.loads((outfitroot/'adoption.json').read_text(encoding='utf-8'))
    outfits=catalog['outfits'];assert catalog['status']=='approved'
    paths=[ROOT/'combinations'/f'{h}-fa-oa.png' for h,n in HAIRS]+[outfitroot/o['frame'] for o in outfits]
    before={str(p.relative_to(ROOT)):digest(p) for p in paths}
    reference=np.asarray(Image.open(ROOT/'combinations/hb-fa-oa.png').convert('RGBA'))
    neutral=np.asarray(Image.open(ROOT/'expression-runtime-v4/frames/00.png').convert('RGBA'))
    face=np.zeros((160,128),bool)
    for l,t,r,b in [(74,52,85,55),(72,55,87,61),(72,61,87,66)]:face[t:b,l:r]=True
    yy,xx=np.indices((160,128))
    face &= yy<65  # Row65 belongs to the outfit's neck/collar, not the fixed head.
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',18)
    small=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',14)
    overview=Image.new('RGB',(1280,1160),'#eee7da');d=ImageDraw.Draw(overview)
    native=Image.new('RGB',(800,680),'#eee7da');dn=ImageDraw.Draw(native)
    seams=Image.new('RGB',(1600,810),'#eee7da');ds=ImageDraw.Draw(seams)
    headchecks={};rows=[];hairinfo=[]
    for col,(hair,title) in enumerate(HAIRS):
        src=np.asarray(Image.open(ROOT/'combinations'/f'{hair}-fa-oa.png').convert('RGBA'))
        delta=np.any(src!=reference,axis=2)
        allowed=delta&(yy<65)&~face
        hairinfo.append({'id':hair,'applied_hair_pixels':int(allowed.sum()),'excluded_neck_collar_differences':int((delta&(yy>=65)).sum()),'protected_face_differences':int((delta&face).sum())})
        for row,outfit in enumerate(outfits):
            basepath=outfitroot/outfit['frame'];base=np.asarray(Image.open(basepath).convert('RGBA')).copy()
            a=base.copy();a[allowed]=src[allowed]
            assert np.array_equal(a[65:],base[65:])
            assert np.array_equal(a[face],neutral[face])
            assert np.array_equal(a[~allowed],base[~allowed])
            assert set(np.unique(a[:,:,3])).issubset({0,255})
            components,_=component_labels(a[:,:,3]>0)
            assert components[57,78]>0 and components[57,78]==components[80,74]
            if hair in headchecks:assert np.array_equal(a[:65],headchecks[hair])
            else:headchecks[hair]=a[:65].copy()
            name=f'{hair}-{outfit["id"]}.png';dest=OUT/'frames'/name
            image=Image.fromarray(a);image.save(dest)
            if hair=='hb':assert dest.read_bytes()==basepath.read_bytes()
            zoom=image.resize((256,320),Image.Resampling.NEAREST)
            overview.paste(zoom,(col*256,row*380+20),zoom)
            d.text((col*256+60,row*380+340),title,font=font,fill='#443d35')
            d.text((col*256+45,row*380+365),outfit['label'],font=small,fill='#443d35')
            native.paste(image,(col*160+16,row*220+10),image)
            dn.text((col*160+30,row*220+177),title,font=small,fill='#443d35')
            dn.text((col*160+8,row*220+200),outfit['label'],font=small,fill='#443d35')
            crop=image.crop((50,48,96,82)).resize((276,204),Image.Resampling.NEAREST)
            seams.paste(crop,(col*320+22,row*270+10),crop)
            ds.text((col*320+40,row*270+230),title+' / '+outfit['label'],font=small,fill='#443d35')
            opaque_y,opaque_x=np.where(a[:,:,3]>0)
            rows.append({'hair':hair,'outfit':outfit['id'],'file':'frames/'+name,'sha256':digest(dest),'canvas':[128,160],'feet_y':int(opaque_y.max()),'body_unchanged':True,'neutral_face_unchanged':True})
    assert len(rows)==15
    assert len({r['sha256'] for r in rows})==15
    assert all(digest(ROOT/p)==sha for p,sha in before.items())
    assert all(r['feet_y']==147 for r in rows)
    overview.save(OUT/'combinations-review.png');native.save(OUT/'native-size.png');seams.save(OUT/'neck-collar-review.png')
    qa={'art_source':'existing','operation':'approved hair delta compositing; no image generation','status':'structural-checks-pass; visual-review-in-visual-review.json','images':15,'hairstyles':5,'outfits':3,'canvas':[128,160],'all15_unique':True,'body_rows_65_onward_byte_identical_to_each_outfit':True,'same_head_for_each_hair_across_outfits':True,'adopted_neutral_face_preserved':True,'short_side_part_matches_approved_outfits_byte_exact':True,'all_feet_y':147,'binary_alpha':True,'head_and_torso_connected_in_all15':True,'source_files_unchanged':True,'hair_masks':hairinfo,'inputs':before,'limits':['neutral front-three-quarter standing pose only','not 8 expressions x 5 hairs x 3 outfits','not universal separated hair/face/clothes layers','no sitting walking or animation validation']}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'catalog.json').write_text(json.dumps({'status':'static-combination-validation','hairstyles':[{'id':h,'name':n} for h,n in HAIRS],'outfits':outfits,'face':'expression-runtime-v4 neutral','images':rows},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in qa.items() if k not in ('inputs','hair_masks')},ensure_ascii=False))
if __name__=='__main__':main()
