"""Prepare hairstyle proposals at game scale while retaining accepted face/body pixels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
def main():
    base=np.asarray(Image.open(ROOT/"combinations/ha-fa-oa.png").convert("RGBA")).copy()
    short=np.asarray(Image.open(ROOT/"combinations/hb-fa-oa.png").convert("RGBA")).copy()
    raw=[Image.open(p).convert("RGBA") for p in sorted((OUT/"keyed/frames").glob("*.png"))]
    yy,xx=np.indices(base.shape[:2])
    face=((xx>=72)&(xx<=85)&(yy>=54)&(yy<68))|((xx>=68)&(xx<72)&(yy>=58)&(yy<65))
    permitted=(yy<68)&~face
    colors=np.array([tuple(bytes.fromhex(c["hex"][1:])) for c in json.loads((ROOT/"idle-finished/palette.json").read_text())["colors"]],dtype=np.int32)
    proposals=[]
    for i,source in enumerate(raw):
        crop=source.crop(source.getbbox())
        # Display proposal: same body height for inspection; never replace approved whole body.
        factor=112/crop.height
        resized=crop.resize((round(crop.width*factor),112),Image.Resampling.BOX)
        a=np.asarray(resized).copy()
        visible=a[:,:,3]>=128
        rgb=a[:,:,:3][visible].astype(np.int32)
        indices=((rgb[:,None,:]-colors[None,:,:])**2).sum(axis=2).argmin(axis=1)
        a[:,:,:3][visible]=colors[indices].astype(np.uint8)
        a[:,:,3]=np.where(visible,255,0)
        a[~visible,:3]=0
        canvas=Image.new("RGBA",(128,160))
        canvas.alpha_composite(Image.fromarray(a),(round(75.5-resized.width/2),36))
        candidate=base.copy();candidate[permitted]=np.asarray(canvas)[permitted]
        assert np.array_equal(candidate[~permitted],base[~permitted])
        assert np.array_equal(candidate[68:],base[68:])
        Image.fromarray(candidate).save(OUT/f"proposal-{i:02}.png")
        proposals.append(candidate)
    variants=[proposals[0],short,proposals[1]]
    labels=["微分碎蓋 · 提案","短偏分 · 已選定","斜瀏海 · 提案"]
    board=Image.new("RGB",(512*3,710),"#eee7da")
    draw=ImageDraw.Draw(board)
    font=ImageFont.truetype("C:/Windows/Fonts/msjh.ttc",22)
    for i,(a,label) in enumerate(zip(variants,labels)):
        im=Image.fromarray(a).resize((512,640),Image.Resampling.NEAREST)
        board.paste(im,(i*512,0),im)
        draw.text((i*512+45,660),label,fill="#443d35",font=font)
    board.save(OUT/"comparison.png")
    qa={"status":"needs-visual-review","approved":"short side-part",
      "proposed":["textured fringe crop","asymmetric diagonal fringe"],
      "same_body_and_protected_face":True,"same_palette":True,"canvas":[128,160],
      "limits":["new hairstyles are static proposals; not installed as approved active combinations",
        "protected face limits fringe overlap","pure hair-only layers and motion not yet authored"]}
    (OUT/"qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    print(json.dumps(qa))
if __name__=="__main__":main()

