"""Build a provisional paper-doll alignment test and GIF from generated PNG art.
Only cuts, registers, composites, quantizes and packages existing art; does not draw poses.
"""
from pathlib import Path
from itertools import product
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SIZE = (128, 160)
ANCHOR = (64, 148)

def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def register_idle():
    source = sorted((ROOT / "idle-keyed/frames").glob("*.png"))
    out = ROOT / "idle-registered"
    out.mkdir(exist_ok=True)
    records = []
    # One source-to-display scale is applied later. Here only translations fix sheet layout.
    ref_anchor = None
    for index, file in enumerate(source):
        image = Image.open(file).convert("RGBA")
        alpha = np.asarray(image.getchannel("A"))
        ys, xs = np.nonzero(alpha > 127)
        baseline = int(ys.max()) + 1
        foot_x = np.nonzero((alpha > 127) & (np.indices(alpha.shape)[0] >= baseline - 12))[1]
        anchor = (int(round((int(foot_x.min()) + int(foot_x.max())) / 2)), baseline)
        if ref_anchor is None:
            ref_anchor = anchor
        delta = (ref_anchor[0] - anchor[0], ref_anchor[1] - anchor[1])
        canvas = Image.new("RGBA", image.size)
        canvas.alpha_composite(image, delta)
        assert canvas.getchannel("A").getextrema()[1] == 255
        assert np.count_nonzero(np.asarray(canvas.getchannel("A"))) == np.count_nonzero(alpha)
        canvas.save(out / f"frame-{index:02}.png")
        records.append({"frame": index, "source_anchor": anchor, "translation": delta})
    save_json(ROOT / "idle-registration.json", {"method": "translation_only_bottom_12px_foot_span", "source_size": [627,627], "reference_anchor": ref_anchor, "frames": records})

def fitted_layer(image, width=None, height=None, xy=(0,0)):
    crop = image.crop(image.getbbox())
    if width is not None:
        scale = width / crop.width
    else:
        scale = height / crop.height
    target = (round(crop.width * scale), round(crop.height * scale))
    crop = crop.resize(target, Image.Resampling.BOX)
    array = np.asarray(crop).copy()
    array[:,:,3] = np.where(array[:,:,3] >= 128, 255, 0)
    array[array[:,:,3] == 0, :3] = 0
    crop = Image.fromarray(array)
    canvas = Image.new("RGBA", SIZE)
    # x is the requested visible-box midpoint, y is the top.
    canvas.alpha_composite(crop, (round(xy[0] - target[0] / 2), xy[1]))
    return canvas

def make_parts():
    paths = sorted((ROOT / "parts-keyed/frames").glob("*.png"))
    raw = [Image.open(p).convert("RGBA") for p in paths]
    # Explicit provisional landmark fitting. No claim of automatic perfect registration.
    layers = {
        "body": fitted_layer(raw[0], height=112, xy=(64,36)),
        "hair-a": fitted_layer(raw[1], width=43, xy=(65,29)),
        "hair-b": fitted_layer(raw[2], width=43, xy=(65,29)),
        "face-a": fitted_layer(raw[3], height=38, xy=(65,36)),
        "face-b": fitted_layer(raw[4], height=38, xy=(65,36)),
        "outfit-a": fitted_layer(raw[5], height=80, xy=(66,68)),
        "outfit-b": fitted_layer(raw[6], height=80, xy=(66,68)),
    }
    folder = ROOT / "layers-standing"
    folder.mkdir(exist_ok=True)
    for name, image in layers.items():
        image.save(folder / f"{name}.png")
    combinations = ROOT / "combinations"
    combinations.mkdir(exist_ok=True)
    board = Image.new("RGB", (128*4*2, 190*2*2), "#f4eee3")
    draw = ImageDraw.Draw(board)
    ids = []
    for index, (hair, face, outfit) in enumerate(product("ab", repeat=3)):
        image = Image.new("RGBA", SIZE)
        for name in ("body", f"outfit-{outfit}", f"face-{face}", f"hair-{hair}"):
            image.alpha_composite(layers[name])
        name = f"h{hair}-f{face}-o{outfit}"
        image.save(combinations / f"{name}.png")
        x, y = (index % 4) * 256, (index // 4) * 380
        board.paste(image.resize((256,320), Image.Resampling.NEAREST), (x,y), image.resize((256,320), Image.Resampling.NEAREST))
        draw.text((x+34,y+328), name, fill="#4a463e")
        ids.append(name)
    board.save(ROOT / "combinations-review.png")
    save_json(ROOT / "paper-doll.json", {
        "status":"prototype-needs-visual-review", "canvas":SIZE, "anchor":ANCHOR,
        "pose":"standing-three-quarter-right", "art_source":"host_image",
        "draw_order":["body","outfit","face","hair"], "hair":["a","b"], "face":["a","b"], "outfit":["a","b"],
        "combinations":ids, "limitations":["provisional manual landmark fit; seams need review",
        "hair is not yet split into front and back layers", "standing only; no motion-specific modular layers",
        "skin tone, gender/body variants and hair recolor not yet authored"]})

def make_gif():
    files = sorted((ROOT / "idle-finished/frames").glob("*.png"))
    frames = [Image.open(file).convert("RGBA") for file in files]
    durations = [1600,350,140,450]
    assert len(frames) == 4 and all(f.size == SIZE for f in frames)
    # One shared preview palette, opaque review background, no dithering.
    previews = []
    for frame in frames:
        bg = Image.new("RGBA",SIZE,"#eee6d8")
        bg.alpha_composite(frame)
        previews.append(bg.convert("RGB").resize((384,480),Image.Resampling.NEAREST))
    palette_source = Image.new("RGB",(384*4,480))
    for i,f in enumerate(previews): palette_source.paste(f,(384*i,0))
    palette = palette_source.quantize(colors=128, dither=Image.Dither.NONE)
    indexed = [f.quantize(palette=palette,dither=Image.Dither.NONE) for f in previews]
    indexed[0].save(ROOT/"idle-preview.gif",save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=False,disposal=2)
    decoded = Image.open(ROOT/"idle-preview.gif")
    actual=[]
    for i in range(decoded.n_frames):
        decoded.seek(i); actual.append(decoded.info["duration"])
    assert decoded.n_frames == 4 and actual == durations, (decoded.n_frames,actual)
    checks={"frame_count":4,"frame_size":SIZE,"anchor":ANCHOR,"gif_durations_ms":actual,
      "gif_loop_ms":sum(actual),"unique_frames":len({f.tobytes() for f in frames}),
      "binary_alpha":all(set(np.asarray(f.getchannel("A")).ravel().tolist()) <= {0,255} for f in frames),
      "visible_palette_colors":[len(np.unique(np.asarray(f)[:,:,:3][np.asarray(f)[:,:,3]>0],axis=0)) for f in frames],
      "status":"prototype-needs-visual-review",
      "limitations":["generated shapes may shimmer; not approved runtime art",
      "idle frames are full-character composites; not yet modular per-frame paper doll layers"]}
    assert checks["unique_frames"] == 4 and checks["binary_alpha"]
    save_json(ROOT/"idle-qa.json",checks)
    clips={"schema":"generate2dsprite.animation_clips.v2",
      "frames":[f"idle-finished/frames/{f.name}" for f in files],"anchor_px":ANCHOR,
      "clips":{"idle":{"frames":[0,1,2,3],"duration_ms":durations,"loop_policy":"cycle"}},
      "states":{"idle":"idle"},"sampling":"nearest","pixel_art":True,"art_source":"host_image","placeholder":True,"body_height_px":112}
    save_json(ROOT/"clips-input.json",clips)
    print(json.dumps(checks))
    
if __name__ == "__main__":
    import sys
    if sys.argv[1] == "prepare":
        raise SystemExit("Deprecated: original independently fitted parts were rejected; do not overwrite current combinations. Use canonical-v3/package_canonical.py.")
    elif sys.argv[1] == "gif":
        make_gif()

