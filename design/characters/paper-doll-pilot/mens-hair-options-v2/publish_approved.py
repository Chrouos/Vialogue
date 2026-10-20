"""Publish the approved hairstyle stills with existing vest palette variants."""
from pathlib import Path
import json,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
def main():
    spec=importlib.util.spec_from_file_location("hair_pack",ROOT/"hair-b-v1/package_hair.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    styles=[("ha","原始髮型",ROOT/"combinations/ha-fa-oa.png"),
            ("hb","短偏分",ROOT/"combinations/hb-fa-oa.png"),
            ("hc","微蓬後梳",OUT/"proposal-00.png"),
            ("hd","微捲短髮",OUT/"proposal-01.png"),
            ("he","低束小髮髻",OUT/"proposal-02.png")]
    images=[]
    for ident,title,path in styles:
        green=np.asarray(Image.open(path).convert("RGBA")).copy()
        blue=module.vest_variant(green)
        for suffix,arr in [("oa",green),("ob",blue)]:
            output=ROOT/"combinations"/f"{ident}-fa-{suffix}.png"
            if ident in ["hc","hd","he"]:
                Image.fromarray(arr).save(output)
            assert np.array_equal(np.asarray(Image.open(output).convert("RGBA")),arr)
        assert np.array_equal(green[:68],blue[:68])
        images.append((ident,title,green,blue))
    assert len(list((ROOT/"combinations").glob("*.png")))==10
    board=Image.new("RGB",(256*5,370*2),"#eee7da")
    draw=ImageDraw.Draw(board);font=ImageFont.truetype("C:/Windows/Fonts/msjh.ttc",16)
    for col,(ident,title,green,blue) in enumerate(images):
        for row,arr in enumerate([green,blue]):
            im=Image.fromarray(arr).resize((256,320),Image.Resampling.NEAREST)
            board.paste(im,(col*256,row*370),im)
            draw.text((col*256+25,row*370+330),title+" / "+["綠背心","藍背心"][row],font=font,fill="#443d35")
    board.save(ROOT/"combinations-review.png")
    catalog={"status":"hairstyle-stills-approved","canvas":[128,160],
      "hairstyles":[{"id":i,"name":t,"standing_files":[f"../combinations/{i}-fa-oa.png",f"../combinations/{i}-fa-ob.png"]} for i,t,*_ in images],
      "faces":1,"outfit_designs":1,"outfit_colors":2,"active_images":10,
      "full_modular_layers_complete":False,"new_hairstyle_animation_complete":False}
    (OUT/"approved-catalog.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"hairstyles":5,"vest_colors":2,"active_images":10,"head_equal_between_vest_colors":True}))
if __name__=="__main__":main()

