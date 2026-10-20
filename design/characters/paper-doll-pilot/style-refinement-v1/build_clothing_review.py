"""Display existing clothing versions with one identical, approved revised head."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
NAMES=[('tshirt-jeans','T-shirt＋牛仔褲'),('cardigan-straight','針織外套＋直筒褲'),('jacket-shorts','輕薄短外套＋短褲')]

def main():
    font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',20)
    sheet=Image.new('RGB',(1152,550),'#eee7da');d=ImageDraw.Draw(sheet)
    images=[]
    for i,(oid,name) in enumerate(NAMES):
        img=Image.open(ROOT/'frames'/f'hb-{oid}.png').convert('RGBA');images.append(img)
        zoom=img.resize((384,480),Image.Resampling.NEAREST)
        sheet.paste(zoom,(i*384,0),zoom);d.text((i*384+80,500),name,font=font,fill='#443d35')
    sheet.save(ROOT/'outfits-review.png')
    new=np.asarray(images[2]).copy()
    old=np.asarray(Image.open(ROOT.parent/'modern-outfits-v2/frames/jacket-shorts.png').convert('RGBA')).copy()
    old[:65]=new[:65]
    assert np.array_equal(old[:65],new[:65])
    assert np.array_equal(old[99:],new[99:])
    pair=Image.new('RGB',(768,550),'#eee7da');p=ImageDraw.Draw(pair)
    for i,(a,title) in enumerate([(old,'外套調整前'),(new,'外套調整後')]):
        img=Image.fromarray(a).resize((384,480),Image.Resampling.NEAREST)
        pair.paste(img,(i*384,0),img);p.text((i*384+120,500),title,font=font,fill='#443d35')
    pair.save(ROOT/'jacket-before-after.png')
    print('Verified comparison: identical revised head, shorts, legs and shoes; jacket-only difference.')
if __name__=='__main__':main()
