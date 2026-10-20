"""Use accepted idle pixels verbatim; only a palette-layer garment variant is derived."""
from pathlib import Path
from shutil import copyfile
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    source=ROOT/"idle-finished/frames/frame-00.png"
    a=np.asarray(Image.open(source).convert("RGBA")).copy()
    b=a.copy()
    # Four actual vest shade groups from the approved idle palette.
    # Replacement colors come from the already-generated navy clothing study.
    pairs=[((84,68,31),(36,43,52)),((110,90,41),(50,61,72)),
           ((124,104,48),(71,83,91)),((139,116,55),(97,110,114))]
    yy,xx=np.indices(a.shape[:2])
    garment=(yy>=68)&(yy<100)&(xx>=58)&(xx<89)&(a[:,:,3]==255)
    mask=np.zeros(a.shape[:2],dtype=bool)
    for old,new in pairs:
        pixels=garment & np.all(a[:,:,:3]==old,axis=2)
        b[pixels,:3]=new
        mask |= pixels
    assert mask.sum()>200
    assert np.array_equal(a[:68],b[:68])
    assert np.array_equal(a[~mask],b[~mask])
    assert np.array_equal(a[:,:,3],b[:,:,3])
    folder=ROOT/"combinations"
    # Byte copy for base: not resized, repaletted, or re-encoded.
    copyfile(source,folder/"ha-fa-oa.png")
    Image.fromarray(b).save(folder/"ha-fa-ob.png")
    copyfile(source,OUT/"accepted-idle-base.png")
    Image.fromarray(b).save(OUT/"navy-variant.png")
    assert sha(folder/"ha-fa-oa.png")==sha(source)
    (OUT/"layers").mkdir(exist_ok=True)
    common=a.copy();common[mask]=0
    colors_a=np.zeros_like(a);colors_a[mask]=a[mask]
    colors_b=np.zeros_like(a);colors_b[mask]=b[mask]
    for name,arr in [("shared-character",common),("vest-moss",colors_a),("vest-navy",colors_b)]:
        Image.fromarray(arr).save(OUT/"layers"/f"{name}.png")
    for layer,expected in [(colors_a,a),(colors_b,b)]:
        rebuilt=Image.alpha_composite(Image.fromarray(common),Image.fromarray(layer))
        assert np.array_equal(np.asarray(rebuilt),expected)
    # Both variants share the same exact accepted head; display native pixels at 4x.
    board=Image.new("RGB",(512*2,690),"#eee7da")
    draw=ImageDraw.Draw(board)
    for index,(label,arr) in enumerate([("ACCEPTED IDLE / ORIGINAL",a),("SAME PIXELS / NAVY VEST",b)]):
        im=Image.fromarray(arr).resize((512,640),Image.Resampling.NEAREST)
        board.paste(im,(index*512,0),im)
        draw.text((index*512+30,654),label,fill="#423d35")
    board.save(ROOT/"combinations-review.png")
    board.save(OUT/"comparison.png")
    report={"status":"needs-visual-review","source":str(source.relative_to(ROOT)),
       "source_sha256":sha(source),"original_variant_byte_identical":True,
       "head_region":[0,0,128,68],"head_region_pixel_identical":True,
       "outside_garment_pixel_identical":True,"alpha_pixel_identical":True,
       "changed_vest_pixels":int(mask.sum()),"canvas":[128,160],
       "resized":False,"repaletted_base":False,"new_generation":False,
       "layer_reconstruction_exact":True,
       "limitations":["one existing hairstyle and face; only vest color variant",
       "not yet full modular paper doll or animated replacement layers"]}
    (OUT/"qa.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report))
if __name__=="__main__":main()

