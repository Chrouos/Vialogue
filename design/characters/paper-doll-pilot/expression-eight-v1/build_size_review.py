"""Size-review approved generated portraits; crops/resampling only, no drawn art."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
LABELS=['一般','開心','超開心','為難','傷心','超傷心','害羞','生氣']

def main():
    source=Image.open(ROOT/'expressions.png').convert('RGB')
    assert source.size==(1254,1254)
    original=hashlib.sha256((ROOT/'expressions.png').read_bytes()).hexdigest()
    out=ROOT/'size-review';out.mkdir(exist_ok=True)
    # Hair and chin fit the same-sized crop; retain intentional head inclines.
    boxes=[]
    for row in range(2):
        for col in range(4):
            left=round(col*1254/4)
            boxes.append((left,132+row*500,left+314,446+row*500))
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',18)
    small=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',14)
    sheets={}
    for size in (32,48,64):
        folder=out/f'{size}px';folder.mkdir(exist_ok=True)
        sheet=Image.new('RGB',(560,240),'#f7f0df');d=ImageDraw.Draw(sheet)
        zoom=Image.new('RGB',(960,640),'#f7f0df');z=ImageDraw.Draw(zoom)
        for i,(box,label) in enumerate(zip(boxes,LABELS)):
            crop=source.crop(box)
            # Area downscale, limited palette, no dithering; previews use nearest.
            icon=crop.resize((size,size),Image.Resampling.BOX).quantize(colors=32,dither=Image.Dither.NONE).convert('RGB')
            icon.save(folder/f'{i:02}.png')
            x=(i%4)*140;y=(i//4)*120
            sheet.paste(icon,(x+(140-size)//2,y+10));d.text((x+35,y+84),label,font=small,fill='#443d35')
            zoom.paste(icon.resize((192,192),Image.Resampling.NEAREST),((i%4)*240+24,(i//4)*320+20))
            z.text(((i%4)*240+70,(i//4)*320+236),label,font=font,fill='#443d35')
        sheet.save(out/f'{size}px-native.png');zoom.save(out/f'{size}px-enlarged.png')
        sheets[str(size)]=f'{size}px-native.png'
    assert hashlib.sha256((ROOT/'expressions.png').read_bytes()).hexdigest()==original
    assert len(list(out.glob('*px/*.png')))==24
    qa={'art_source':'existing','generation_route':'host_image (approved expressions.png)','source_sha256':original,'source_unchanged':True,'sizes':[32,48,64],'portraits':24,'source_crop_boxes':boxes,'sampling':'BOX reduction, nearest enlargement','palette':'32 colors per icon, no dithering','status':'size feasibility review; not game face layers','limits':['32px loses subtle blush, tear and mouth detail','crops include existing opaque ivory background','no animations or paper-doll integration','no changes to approved full-body sprites']}
    (out/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'portraits':24,'source_unchanged':True,'sizes':[32,48,64]}))
if __name__=='__main__':main()
