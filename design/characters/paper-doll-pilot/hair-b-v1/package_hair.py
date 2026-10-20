"""Package hair B using accepted idle geometry; protect face and the entire body."""
from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
DURATIONS=[1600,350,140,450]
def vest_variant(a):
    b=a.copy()
    yy,xx=np.indices(a.shape[:2])
    region=(yy>=68)&(yy<100)&(xx>=58)&(xx<89)&(a[:,:,3]==255)
    for old,new in [((84,68,31),(36,43,52)),((110,90,41),(50,61,72)),
                    ((124,104,48),(71,83,91)),((139,116,55),(97,110,114))]:
        mask=region&np.all(a[:,:,:3]==old,axis=2)
        b[mask,:3]=new
    return b
def main():
    (OUT/"frames").mkdir(exist_ok=True)
    old=[np.asarray(Image.open(p).convert("RGBA")).copy() for p in sorted((ROOT/"idle-finished/frames").glob("*.png"))]
    edited=[np.asarray(Image.open(p).convert("RGBA")).copy() for p in sorted((OUT/"finished/frames").glob("*.png"))]
    assert len(old)==len(edited)==4
    yy,xx=np.indices(old[0].shape[:2])
    # Restore established visible eyes, eyebrow, mouth, jaw and part of the ear.
    face=((xx>=72)&(xx<=85)&(yy>=54)&(yy<68))|((xx>=68)&(xx<72)&(yy>=58)&(yy<65))
    allowed=(yy<68)&~face
    result=[]
    for index,(base,edit) in enumerate(zip(old,edited)):
        frame=base.copy();frame[allowed]=edit[allowed]
        assert np.array_equal(frame[~allowed],base[~allowed])
        assert np.array_equal(frame[68:],base[68:])
        assert np.array_equal(frame[face],base[face])
        assert set(frame[:,:,3].ravel())<={0,255}
        Image.fromarray(frame).save(OUT/"frames"/f"frame-{index:02}.png")
        result.append(frame)
    # Keep approved hair-A images intact. Publish hair-B at the same active folder.
    for suffix,a in [("oa",result[0]),("ob",vest_variant(result[0]))]:
        Image.fromarray(a).save(ROOT/"combinations"/f"hb-fa-{suffix}.png")
    originals=[np.asarray(Image.open(ROOT/"combinations"/name).convert("RGBA"))
       for name in ["ha-fa-oa.png","ha-fa-ob.png"]]
    assert np.array_equal(originals[0],old[0])
    assert np.array_equal(originals[1],vest_variant(old[0]))
    arrays=originals+[result[0],vest_variant(result[0])]
    labels=["HAIR A / MOSS","HAIR A / NAVY","HAIR B / MOSS","HAIR B / NAVY"]
    board=Image.new("RGB",(384*4,520),"#eee7da")
    draw=ImageDraw.Draw(board)
    for i,(a,label) in enumerate(zip(arrays,labels)):
        im=Image.fromarray(a).resize((384,480),Image.Resampling.NEAREST)
        board.paste(im,(i*384,0),im)
        draw.text((i*384+32,490),label,fill="#423d35")
    board.save(ROOT/"combinations-review.png")
    board.save(OUT/"comparison.png")
    # One shared GIF palette, no dithering, opaque review background.
    displays=[]
    for a in result:
        bg=Image.new("RGBA",(128,160),"#eee7da")
        bg.alpha_composite(Image.fromarray(a))
        displays.append(bg.convert("RGB").resize((384,480),Image.Resampling.NEAREST))
    allframes=Image.new("RGB",(384*4,480))
    for i,im in enumerate(displays):allframes.paste(im,(i*384,0))
    pal=allframes.quantize(colors=64,dither=Image.Dither.NONE)
    gif=[im.quantize(palette=pal,dither=Image.Dither.NONE) for im in displays]
    gif[0].save(OUT/"idle-preview.gif",save_all=True,append_images=gif[1:],
       duration=DURATIONS,loop=0,optimize=False,disposal=2)
    decoded=Image.open(OUT/"idle-preview.gif")
    assert decoded.n_frames==4
    times=[]
    for i in range(decoded.n_frames):decoded.seek(i);times.append(decoded.info["duration"])
    assert times==DURATIONS
    qa={"status":"needs-visual-review","reference":"../idle-finished",
        "source":"source.png","art_source":"host_image","canvas":[128,160],
        "same_scale":True,"scale":0.20289855,"same_palette":True,
        "body_below_y68_pixel_identical_all_frames":True,
        "protected_visible_face_pixel_identical_all_frames":True,
        "hair_a_base_byte_sha256":hashlib.sha256((ROOT/"combinations/ha-fa-oa.png").read_bytes()).hexdigest(),
        "four_active_combinations":len(list((ROOT/"combinations").glob("*.png"))),
        "changed_pixels":[int(np.any(a!=b,axis=2).sum()) for a,b in zip(old,result)],
        "gif_frames":decoded.n_frames,"gif_durations_ms":times,
        "binary_alpha":True,
        "limits":["hair B is a scoped head replacement patch, not a universal hair-only layer for arbitrary faces",
                  "standing/idle only; other directions and seated pose not yet authored",
                  "new hairstyle and animation still require visual approval"]}
    (OUT/"qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    clips={"schema":"generate2dsprite.animation_clips.v2",
      "frames":[f"frames/frame-{i:02}.png" for i in range(4)],"anchor_px":[64,148],
      "clips":{"idle":{"frames":[0,1,2,3],"duration_ms":DURATIONS,"loop_policy":"cycle"}},
      "states":{"idle":"idle"},"sampling":"nearest","pixel_art":True,"art_source":"host_image","placeholder":True}
    (OUT/"clips-input.json").write_text(json.dumps(clips,indent=2),encoding="utf-8")
    print(json.dumps(qa))
if __name__=="__main__":main()

