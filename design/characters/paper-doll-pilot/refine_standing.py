"""Re-register existing paper-doll art to the user-selected idle proportions.
Sprite processing only: no new generated poses, no changes to accepted idle frames.
All revision outputs are versioned; source files are preserved.
"""
from pathlib import Path
from itertools import product
import json
import numpy as np
from PIL import Image, ImageDraw
from build_pilot import fitted_layer

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "standing-v2"
SIZE = (128,160)
REFERENCE = ROOT / "idle-finished/frames/frame-00.png"

def recolor_to_shared_palette(image, colors):
    arr = np.asarray(image).copy()
    visible = arr[:,:,3] > 127
    pixels = arr[:,:,:3][visible].astype(np.int32)
    palette = np.asarray(colors, dtype=np.int32)
    nearest = ((pixels[:,None,:] - palette[None,:,:]) ** 2).sum(axis=2).argmin(axis=1)
    arr[:,:,:3][visible] = palette[nearest].astype(np.uint8)
    arr[:,:,3] = np.where(visible,255,0).astype(np.uint8)
    arr[~visible,:3] = 0
    return Image.fromarray(arr)

def main():
    OUT.mkdir(exist_ok=True)
    raw = [Image.open(p).convert("RGBA") for p in sorted((ROOT/"parts-keyed/frames").glob("*.png"))]
    # A common body baseline and explicit head landmarks replace independent bbox fits.
    body = fitted_layer(raw[0],height=112,xy=(75,36))
    arr = np.asarray(body).copy()
    arr[:68,:,:] = 0 # the replacement face owns the head/neck, not an overlapping bald base
    body = Image.fromarray(arr)
    layers = {
        "body":body,
        "hair-a":fitted_layer(raw[1],width=34,xy=(75,36)),
        "hair-b":fitted_layer(raw[2],width=34,xy=(75,36)),
        "face-a":fitted_layer(raw[3],height=27,xy=(76,43)),
        "face-b":fitted_layer(raw[4],height=27,xy=(76,43)),
        "outfit-a":fitted_layer(raw[5],height=80,xy=(77,68)),
        "outfit-b":fitted_layer(raw[6],height=80,xy=(77,68)),
    }
    colors = [tuple(bytes.fromhex(c["hex"][1:])) for c in json.loads((ROOT/"idle-finished/palette.json").read_text())["colors"]]
    # Outfit B needs navy; extend the same shading palette rather than removing blue clothing.
    colors += [(36,43,52),(50,61,72),(71,83,91),(97,110,114)]
    layers = {key:recolor_to_shared_palette(im,colors) for key,im in layers.items()}
    (OUT/"layers").mkdir(exist_ok=True)
    (OUT/"combinations").mkdir(exist_ok=True)
    for key,im in layers.items(): im.save(OUT/"layers"/f"{key}.png")
    all_combos=[]
    for h,f,o in product("ab",repeat=3):
        im = Image.new("RGBA",SIZE)
        for key in ("body",f"outfit-{o}",f"face-{f}",f"hair-{h}"): im.alpha_composite(layers[key])
        name=f"h{h}-f{f}-o{o}"
        im.save(OUT/"combinations"/f"{name}.png")
        all_combos.append((name,im))
    bg="#e9e3d6"
    board=Image.new("RGB",(256*5,360*2),bg)
    draw=ImageDraw.Draw(board)
    reference=Image.open(REFERENCE).convert("RGBA")
    old=Image.open(ROOT/"combinations/ha-fa-ob.png").convert("RGBA")
    items=[("APPROVED IDLE",reference)]+all_combos[:4]+[("PREVIOUS FIT",old)]+all_combos[4:]
    for index,(name,im) in enumerate(items):
        x,y=(index%5)*256,(index//5)*360
        zoom=im.resize((256,320),Image.Resampling.NEAREST)
        board.paste(zoom,(x,y),zoom)
        draw.text((x+20,y+326),name,fill="#423d35")
    board.save(OUT/"comparison.png")
    bboxes={name:list(im.getbbox()) for name,im in all_combos}
    ref_bbox=reference.getbbox()
    assert all(im.size==SIZE for _,im in all_combos)
    assert all(b[3]==148 and b[3]-b[1]==112 for b in bboxes.values()), bboxes
    assert layers["hair-a"].getbbox()[2]-layers["hair-a"].getbbox()[0] == 34
    assert all(set(np.asarray(im)[:,:,3].ravel()) <= {0,255} for _,im in all_combos)
    # All hair/face options must produce actual distinct composites with each outfit.
    assert len({im.tobytes() for _,im in all_combos})==8
    report={"status":"needs-visual-review","reference":"../idle-finished/frames/frame-00.png",
      "canvas":SIZE,"reference_bbox":ref_bbox,"reference_height":ref_bbox[3]-ref_bbox[1],
      "old_height":old.getbbox()[3]-old.getbbox()[1],"new_height":112,
      "hair_width_before":43,"hair_width_after":34,"face_height_before":38,"face_height_after":27,
      "same_reference_palette":True,"extra_outfit_colors":4,"palette_colors":len(colors),
      "all_eight_unique":True,"binary_alpha":True,"bboxes":bboxes,
      "limitations":["source parts are independently generated: anatomy/pose still differ from reference",
      "standing only; clothes and neck joins require visual review",
      "not final modular animation; accepted idle frames were preserved"]}
    (OUT/"qa.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report))
if __name__=="__main__": main()

