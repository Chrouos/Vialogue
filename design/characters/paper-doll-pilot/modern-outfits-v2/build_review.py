"""Key generated clothing, area-reduce and composite the approved head unchanged."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
NAMES=['T-shirt＋牛仔褲','針織外套＋直筒褲','短外套＋短褲']
IDS=['tshirt-jeans','cardigan-straight','jacket-shorts']

def main():
    source=Image.open(OUT/'source.png').convert('RGB')
    assert source.size==(1536,1024)
    basepath=ROOT/'expression-runtime-v4/frames/00.png'
    base=np.asarray(Image.open(basepath).convert('RGBA')).copy()
    original=hashlib.sha256(basepath.read_bytes()).hexdigest()
    raw=[]
    for i in range(3):
        a=np.asarray(source.crop((i*512,192,(i+1)*512,832))).astype(float)
        key=(a[:,:,0]>170)&(a[:,:,1]<115)&(a[:,:,2]>145)
        alpha=(~key).astype(float)
        coverage=np.asarray(Image.fromarray(alpha.astype('float32')).resize((128,160),Image.Resampling.BOX))
        rgb=np.zeros((160,128,3))
        for c in range(3):
            channel=np.asarray(Image.fromarray((a[:,:,c]*alpha).astype('float32')).resize((128,160),Image.Resampling.BOX))
            rgb[:,:,c]=channel/np.maximum(coverage,1e-6)
        rgba=np.zeros((160,128,4),dtype=np.uint8)
        rgba[:,:,:3]=np.clip(rgb,0,255).astype(np.uint8);rgba[:,:,3]=(coverage>=.5)*255
        raw.append(rgba)
    # One shared body palette; preserve every approved head colour exactly.
    pixels=np.concatenate([a[65:,:,:3][a[65:,:,3]>0] for a in raw])
    colors=Image.fromarray(pixels.reshape(1,-1,3)).quantize(colors=40,dither=Image.Dither.NONE)
    palette=colors.getpalette()
    palette_image=Image.new('P',(1,1));palette_image.putpalette(palette)
    (OUT/'frames').mkdir(exist_ok=True)
    review=Image.new('RGB',(1152,550),'#eee7da');d=ImageDraw.Draw(review)
    native=Image.new('RGB',(576,205),'#eee7da');dn=ImageDraw.Draw(native)
    compare=Image.new('RGB',(1536,550),'#eee7da');dc=ImageDraw.Draw(compare)
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',20)
    small=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',15)
    old=Image.fromarray(base).resize((384,480),Image.Resampling.NEAREST)
    compare.paste(old,(0,0),old);dc.text((120,500),'原款背心',font=font,fill='#443d35')
    stats=[]
    for i,(a,name,assetid) in enumerate(zip(raw,NAMES,IDS)):
        quant=np.asarray(Image.fromarray(a[:,:,:3]).quantize(palette=palette_image,dither=Image.Dither.NONE).convert('RGB'))
        a[:,:,:3]=quant
        a[:65]=base[:65]
        a[a[:,:,3]==0,:3]=0
        previous=ROOT/'modern-outfits-v1/frames'
        if i==0:
            old=np.asarray(Image.open(previous/'shirt-jeans.png').convert('RGBA'))
            a[103:]=old[103:]
        elif i==1:
            a=np.asarray(Image.open(previous/'cardigan-straight.png').convert('RGBA')).copy()
        else:
            old=np.asarray(Image.open(previous/'jacket-wide.png').convert('RGBA'))
            a[65:99]=old[65:99]
            a[139:]=old[139:]
        assert np.array_equal(a[:65],base[:65])
        assert set(np.unique(a[:,:,3])).issubset({0,255})
        image=Image.fromarray(a);image.save(OUT/'frames'/f'{assetid}.png')
        if i==1:
            assert (OUT/'frames'/f'{assetid}.png').read_bytes()==(previous/'cardigan-straight.png').read_bytes()
        zoom=image.resize((384,480),Image.Resampling.NEAREST)
        review.paste(zoom,(i*384,0),zoom);d.text((i*384+80,500),name,font=font,fill='#443d35')
        compare.paste(zoom,((i+1)*384,0),zoom);dc.text(((i+1)*384+80,500),name,font=font,fill='#443d35')
        native.paste(image,(i*192+32,0),image);dn.text((i*192+18,175),name,font=small,fill='#443d35')
        yy,xx=np.where(a[:,:,3]>0)
        stats.append({'id':assetid,'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'lowest_pixel':int(yy.max()),'colors':len(np.unique(a[a[:,:,3]>0,:3],axis=0))})
    review.save(OUT/'outfits-review.png');native.save(OUT/'native-size.png');compare.save(OUT/'with-original.png')
    assert hashlib.sha256(basepath.read_bytes()).hexdigest()==original
    (OUT/'body-palette.json').write_text(json.dumps({'colors':[list(palette[i:i+3]) for i in range(0,120,3)],'reserved_head':'approved pixels kept byte-exact; not quantized'},indent=2),encoding='utf-8')
    qa={'art_source':'host_image','status':'needs-user-visual-review','canvas':[128,160],'head_rows':[0,65],'approved_head_byte_identical':True,'original_base_unchanged':True,'binary_alpha':True,'cardigan_byte_identical_to_v1':True,'first_jeans_rows_preserved':[103,160],'third_jacket_rows_preserved':[65,99],'third_shoes_rows_preserved':[139,160],'sampling':'premultiplied BOX, shared40 newbody colors, existing pixels preserved, no dithering','outfits':stats,'limits':['three static full outfits, not separated clothing layers','only short side part and neutral expression preview','not animated; not approved yet','preserved garments retain their previous palette']}
    (OUT/'qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
    print(json.dumps(qa))
if __name__=='__main__':main()
