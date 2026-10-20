"""Reduce generated facial ink with coverage preservation so tiny curves remain readable."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
PILOT=ROOT.parent
def main():
    source=np.asarray(Image.open(ROOT/"registered/frame-00.png").convert("RGBA"))
    result=np.asarray(Image.open(ROOT/"finished/frames/frame-00.png").convert("RGBA")).copy()
    palette=np.array([tuple(bytes.fromhex(c["hex"][1:])) for c in json.loads((PILOT/"idle-finished/palette.json").read_text())["colors"]],dtype=float)
    ref=json.loads((PILOT/"idle-finished/finish.json").read_text())
    scale=ref["scale"];ax,ay=ref["anchorSource"];tx,ty=ref["anchor"]
    regions=[(72,53,80,61),(82,53,87,60),(77,61,85,66)]
    for l,t,r,b in regions:
        for y in range(t,b):
            for x in range(l,r):
                x0=int(np.floor(ax+(x-tx)/scale));x1=int(np.ceil(ax+(x+1-tx)/scale))
                y0=int(np.floor(ay+(y-ty)/scale));y1=int(np.ceil(ay+(y+1-ty)/scale))
                pixels=source[y0:y1,x0:x1,:3].reshape(-1,3).astype(float)
                luma=pixels@np.array([.2126,.7152,.0722])
                ink=luma<90
                # Static facial linework only; no model redraw or whole-body resampling.
                if ink.mean()>=.20:
                    color=pixels[ink].mean(axis=0)
                else:
                    color=pixels.mean(axis=0)
                best=((palette-color)**2).sum(axis=1).argmin()
                result[y,x,:3]=palette[best].astype(np.uint8)
    Image.fromarray(result).save(ROOT/"face-detail.png")
if __name__=="__main__":main()

