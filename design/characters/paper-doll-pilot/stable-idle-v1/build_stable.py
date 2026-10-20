"""Stable pixel animation from one fixed approved hairstyle-B sprite.
No generated per-frame hair texture is used.
"""
from pathlib import Path
from shutil import copyfile
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
HAIR=ROOT/"hair-b-v1"
OUT=Path(__file__).resolve().parent
TIMES=[1600,450,100,650]
def main():
    OUT.mkdir(exist_ok=True)
    (OUT/"frames").mkdir(exist_ok=True)
    base=np.asarray(Image.open(ROOT/"combinations/hb-fa-oa.png").convert("RGBA")).copy()
    closed=np.asarray(Image.open(ROOT/"idle-finished/frames/frame-02.png").convert("RGBA"))
    yy,xx=np.indices(base.shape[:2])
    eye=((xx>=72)&(xx<=78)&(yy>=55)&(yy<=59))|((xx>=83)&(xx<=85)&(yy>=54)&(yy<=57))
    blink=base.copy();blink[eye]=closed[eye]
    def breathe(a):
        b=a.copy()
        # One coherent pixel translation above the ankles, stationary footwear.
        b[:127]=a[1:128]
        b[127]=a[127]
        return b
    raised=breathe(base)
    blink_raised=breathe(blink)
    frames=[base,raised,blink_raised,base.copy()]
    assert np.array_equal(frames[0],frames[3])
    assert np.array_equal(frames[1][:127],base[1:128])
    assert np.array_equal(frames[2][128:],base[128:])
    # Undo the known translation and compare every non-eye pixel: zero texture drift.
    non_eye=~eye[1:128]
    assert np.array_equal(frames[2][:127][non_eye],base[1:128][non_eye])
    assert all(np.array_equal(a[128:],base[128:]) for a in frames)
    for i,a in enumerate(frames):Image.fromarray(a).save(OUT/"frames"/f"frame-{i:02}.png")
    contact=Image.new("RGB",(384*4,520),"#eee7da")
    draw=ImageDraw.Draw(contact)
    displays=[]
    for i,a in enumerate(frames):
        b=Image.new("RGBA",(128,160),"#eee7da");b.alpha_composite(Image.fromarray(a))
        z=b.convert("RGB").resize((384,480),Image.Resampling.NEAREST)
        displays.append(z);contact.paste(z,(i*384,0))
        draw.text((i*384+28,490),f"{i} / {TIMES[i]}ms",fill="#423d35")
    contact.save(OUT/"contact-sheet.png")
    strip=Image.new("RGB",(384*4,480))
    for i,a in enumerate(displays):strip.paste(a,(i*384,0))
    palette=strip.quantize(colors=64,dither=Image.Dither.NONE)
    gifs=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in displays]
    gifs[0].save(OUT/"idle-preview.gif",save_all=True,append_images=gifs[1:],duration=TIMES,loop=0,optimize=False,disposal=2)
    decoded=Image.open(OUT/"idle-preview.gif");actual=[]
    for i in range(decoded.n_frames):decoded.seek(i);actual.append(decoded.info["duration"])
    assert decoded.n_frames==4 and actual==TIMES
    previous=OUT/"previous-generated-idle.gif"
    if not previous.exists():copyfile(HAIR/"idle-preview.gif",previous)
    copyfile(OUT/"idle-preview.gif",HAIR/"idle-preview.gif")
    qa={"status":"needs-visual-review","method":"single-fixed-sprite + one-pixel upper-body translation + transferred existing blink patch",
        "generated_pose_texture_used":False,"pose_offsets":[[0,0],[0,-1],[0,-1],[0,0]],
        "fixed_boot_region":[0,128,128,160],"texture_drift_after_pose_compensation":0,
        "hair_texture_identical_after_pose_compensation":True,
        "blink_bounds":[[72,55,79,60],[83,54,86,58]],
        "gif_frames":4,"durations_ms":actual,"canvas":[128,160],
        "loop_last_frame_equals_first":True,"limitations":["prototype one-pixel breathing; not physically articulated chest motion",
          "blink uses a small patch from the accepted closed-eye frame","needs playback review for cadence and ankle join"]}
    (OUT/"qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    manifest={"schema":"generate2dsprite.animation_clips.v2","frames":[f"frames/frame-{i:02}.png" for i in range(4)],
      "anchor_px":[64,148],"clips":{"idle":{"frames":[0,1,2,3],"duration_ms":TIMES,"loop_policy":"cycle"}},
      "states":{"idle":"idle"},"sampling":"nearest","pixel_art":True,"art_source":"existing","placeholder":True}
    (OUT/"clips-input.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(qa))
if __name__=="__main__":main()

