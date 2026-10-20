"""Package canonical outfit variants; preserve the approved identity pixel for pixel."""
from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
BASE=ROOT/"finished/frames"
def main():
    a=np.asarray(Image.open(BASE/"frame-00.png").convert("RGBA")).copy()
    b=np.asarray(Image.open(BASE/"frame-01.png").convert("RGBA")).copy()
    palette=json.loads((ROOT/"palette.json").read_text())["colors"][-4:]
    navy=np.array([tuple(bytes.fromhex(x["hex"][1:])) for x in palette])
    color_mask=(b[:,:,:3,None] == navy.T[None,None,:,:]).all(axis=2).any(axis=2)
    yy,xx=np.indices(a.shape[:2])
    # Explicit garment region: leave head/neck, hands, trousers and footwear immutable.
    mask=color_mask & (yy>=67) & (yy<99) & (xx>=57) & (xx<=87) & (a[:,:,3]>127)
    assert mask.sum()>100, int(mask.sum())
    variant=a.copy(); variant[mask]=b[mask]
    body=a.copy(); body[mask]=0
    vest_a=np.zeros_like(a);vest_a[mask]=a[mask]
    vest_b=np.zeros_like(a);vest_b[mask]=variant[mask]
    (ROOT/"layers").mkdir(exist_ok=True)
    for name,arr in [("body-with-shared-hair-face",body),("vest-moss",vest_a),("vest-navy",vest_b)]:
        Image.fromarray(arr).save(ROOT/"layers"/f"{name}.png")
    out=ROOT.parent/"combinations"
    assert out.is_dir()
    for name,arr in [("ha-fa-oa",a),("ha-fa-ob",variant)]:
        Image.fromarray(arr).save(out/f"{name}.png")
    # Prove that actual layers reconstruct both pixels exactly.
    for vest,expected in [(vest_a,a),(vest_b,variant)]:
        combo=Image.alpha_composite(Image.fromarray(body),Image.fromarray(vest))
        assert np.array_equal(np.asarray(combo),expected)
    assert np.array_equal(a[:67],variant[:67])
    assert np.array_equal(a[~mask],variant[~mask])
    assert np.array_equal(a[:,:,3],variant[:,:,3])
    idle=Image.open(ROOT.parent/"idle-finished/frames/frame-00.png").convert("RGBA")
    originals=[Image.fromarray(a),Image.fromarray(variant),idle]
    labels=["MASTER / MOSS","SHARED HEAD / NAVY","APPROVED IDLE"]
    contact=Image.new("RGB",(384*3,520),"#eee7da")
    draw=ImageDraw.Draw(contact)
    for i,(im,label) in enumerate(zip(originals,labels)):
        zoom=im.resize((384,480),Image.Resampling.NEAREST)
        contact.paste(zoom,(384*i,0),zoom)
        draw.text((384*i+38,488),label,fill="#443d35")
    contact.save(ROOT.parent/"combinations-review.png")
    contact.save(ROOT/"comparison.png")
    qa={"status":"needs-visual-review","canvas":[128,160],
      "variant_type":"vest-color-only","shared_hair_and_face_pixel_identical":True,
      "unchanged_outside_garment_mask":True,"silhouette_identical":True,
      "actual_layer_reconstruction_exact":True,"changed_pixels":int(mask.sum()),
      "height":Image.fromarray(a).getbbox()[3]-Image.fromarray(a).getbbox()[1],
      "limitations":["one hairstyle and face only; full-body base still includes other clothes",
      "two vest colors, not two complete distinct clothing designs",
      "no new hair/face variants or modular animated layers"]}
    (ROOT/"qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    print(json.dumps(qa))
if __name__=="__main__":
    raise SystemExit("Superseded: master-derived small sprites were rejected for face readability. Run idle-base-v4/package_idle_base.py instead.")

