"""Recolor approved pixels through stored hair mattes; never regenerate heads."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.paper_doll import compose,load_catalog
ASSETS=ROOT/'assets/characters/traveler'
REVIEW=ROOT/'design/characters/paper-doll-pilot/hair-colors-v1'
STYLES={'ha':'原始髮型','hb':'短偏分','hc':'俐落後梳','hd':'蓬鬆微捲','he':'低束小髮髻'}
COLORS={'coffee':('咖啡色',None),'black':('黑色',['0e0e12','1c1d22','30313a','494a54','666572']),
        'gray':('灰色',['24242b','494953','777780','a6a5ae','ceccd1']),
        'golden':('金黃色',['302018','614022','9c6d30','ce9e4d','ebcb7c']),
        'rose-red':('玫瑰粉（偏紅）',['34181c','6b2d36','a84250','d66473','ec929e'])}

def recolor(source,mask,ramp):
    result=source.copy()
    if ramp is None:return result
    stops=np.array([int(h[i:i+2],16) for h in ramp for i in (0,2,4)]).reshape(-1,3)
    # One shared lookup per palette: equal source colors stay equal across all haircuts.
    light=source[:,:,:3].astype(float)@np.array([.299,.587,.114])
    mapped=np.stack([np.interp(light,[8,35,65,100,145],stops[:,i]) for i in range(3)],axis=-1)
    result[mask,:3]=np.rint(mapped[mask]).astype(np.uint8)
    return result

def main():
    REVIEW.mkdir(parents=True,exist_ok=True)
    masks=ASSETS/'masks/hair';masks.mkdir(parents=True,exist_ok=True)
    matte=Image.open(REVIEW/'matte-source.png').convert('L').resize((1536,1024))
    variants=[];counts={}
    for index,(style,label) in enumerate(STYLES.items()):
        source=np.array(Image.open(ASSETS/f'layers/head/{style}.png').convert('RGBA'))
        col,row=index%3,index//3
        patch=np.array(matte.crop((col*512+124,row*512+120,col*512+388,row*512+330)).resize((44,35),Image.Resampling.BOX))
        mask=np.zeros((160,128),bool);mask[34:69,52:96]=patch>=128
        mask &= source[:,:,3]>0
        # The approved lower face, eyes and exposed ear are immutable, even if a
        # generated matte is one pixel off at these boundaries.
        mask[65:]=False
        mask[60:65,71:]=False
        mask[56:59,73:77]=False;mask[55:59,83:85]=False
        Image.fromarray((mask*255).astype('uint8')).save(masks/f'{style}.png')
        counts[style]=int(mask.sum())
        for color,(color_label,ramp) in COLORS.items():
            vid=style if color=='coffee' else f'{style}-{color}'
            file=f'layers/head/{vid}.png'
            if color!='coffee':Image.fromarray(recolor(source,mask,ramp)).save(ASSETS/file)
            variants.append({'id':vid,'label':f'{label}／{color_label}','file':file,
                             'selection':{'hairstyle':style,'color':color}})
    catalog_path=ASSETS/'catalog.json';catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
    slot=next(s for s in catalog['slots'] if s['id']=='head')
    stock=set(STYLES)|{f'{s}-{c}' for s in STYLES for c in COLORS if c!='coffee'}
    slot['variants']=variants+[v for v in slot['variants'] if v['id'] not in stock]
    slot['selectors']=[{'key':'hairstyle','label':'髮型','options':[{'id':s,'label':l} for s,l in STYLES.items()]},
                       {'key':'color','label':'髮色','options':[{'id':c,'label':v[0]} for c,v in COLORS.items()]}]
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    palette_path=REVIEW/'palettes.json'
    previous=json.loads(palette_path.read_text(encoding='utf-8')) if palette_path.exists() else {}
    unchanged=previous.get('colors')==json.loads(json.dumps(COLORS))
    status=previous.get('status','pending-visual-review') if unchanged else 'pending-visual-review'
    (REVIEW/'palettes.json').write_text(json.dumps({'status':status,'source':'approved coffee pixels',
        'luminance_stops':[8,35,65,100,145],'colors':COLORS,'masks':counts},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cat=load_catalog(catalog_path)
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',18)
    sheet=Image.new('RGB',(1260,1120),'#eee7da');draw=ImageDraw.Draw(sheet)
    for col,(color,(label,_)) in enumerate(COLORS.items()):
        draw.text((col*252+36,15),label,font=font,fill='#4c473e')
        for row,(style,style_label) in enumerate(STYLES.items()):
            vid=style if color=='coffee' else f'{style}-{color}'
            head=Image.open(ASSETS/f'layers/head/{vid}.png').convert('RGBA').crop((49,31,99,67)).resize((200,144),Image.Resampling.NEAREST)
            sheet.paste(head,(col*252+26,row*210+58),head)
            draw.text((col*252+30,row*210+205),style_label,font=font,fill='#4c473e')
    sheet.save(REVIEW/'hair-colors-review.png')
    full=Image.new('RGBA',(128*5,160*3),'#eee7da')
    for col,color in enumerate(COLORS):
        for row,outfit in enumerate(('tshirt-jeans','cardigan-straight','jacket-shorts')):
            head='hb' if color=='coffee' else f'hb-{color}'
            image=compose(cat,{'head':head,'outfit':outfit});full.alpha_composite(image,(col*128,row*160))
    full.resize((1280,960),Image.Resampling.NEAREST).save(REVIEW/'outfits-colors-review.png')
    provenance=json.loads((ASSETS/'provenance.json').read_text(encoding='utf-8'))
    provenance['hair_colors']={'status':status,'tool':'tools/build_hair_colors.py',
        'matte_source':'design/characters/paper-doll-pilot/hair-colors-v1/matte-source.png',
        'matte_sha256':hashlib.sha256((REVIEW/'matte-source.png').read_bytes()).hexdigest(),
        'art_source':'existing approved pixels; built-in image_gen semantic matte; palette LUT',
        'head_variants':25,'outfit_combinations':75,'fine_layers_complete':False}
    (ASSETS/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'head_variants':25,'combinations':75,'mask_pixels':counts}))

if __name__=='__main__':main()
