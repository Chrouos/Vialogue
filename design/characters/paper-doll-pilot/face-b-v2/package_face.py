"""Compose a proposed second face without modifying approved hairstyle/body pixels."""
from pathlib import Path
from shutil import copyfile
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
def main():
    edited=np.asarray(Image.open(OUT/"face-detail.png").convert("RGBA")).copy()
    yy,xx=np.indices(edited.shape[:2])
    regions=[
      (72,53,80,61), # visible near-side brow/eye
      (82,53,87,60), # small far-side brow/eye
      (77,61,85,66), # tiny mouth
    ]
    mask=np.zeros(edited.shape[:2],dtype=bool)
    for l,t,r,b in regions:mask[t:b,l:r]=True
    (OUT/"combinations").mkdir(exist_ok=True)
    original_hashes={}
    styles=[("ha","原始髮型"),("hb","短偏分"),("hc","微蓬後梳"),("hd","微捲短髮"),("he","低束小髮髻")]
    board=Image.new("RGB",(256*5,370*2),"#eee7da")
    heads=Image.new("RGB",(260*5,270*2),"#eee7da")
    draw=ImageDraw.Draw(board);head_draw=ImageDraw.Draw(heads)
    font=ImageFont.truetype("C:/Windows/Fonts/msjh.ttc",16)
    reports=[]
    for i,(style,title) in enumerate(styles):
        for color in ["oa","ob"]:
            source=ROOT/"combinations"/f"{style}-fa-{color}.png"
            original_hashes[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
            a=np.asarray(Image.open(source).convert("RGBA")).copy()
            b=a.copy();visible_mask=mask & (a[:,:,3]>127) & (edited[:,:,3]>127);b[visible_mask,:3]=edited[visible_mask,:3]
            # Never replace visible hair with candidate eye pixels: edit is confined to established feature rectangles.
            assert np.array_equal(a[~mask],b[~mask])
            assert np.array_equal(a[:,:,3],b[:,:,3])
            assert np.any(a!=b,axis=2).sum()>=3
            copyfile(source,OUT/"combinations"/source.name)
            Image.fromarray(b).save(OUT/"combinations"/f"{style}-fb-{color}.png")
            if color=="oa":
                for row,arr in enumerate([a,b]):
                    im=Image.fromarray(arr)
                    z=im.resize((256,320),Image.Resampling.NEAREST)
                    board.paste(z,(i*256,row*370),z)
                    draw.text((i*256+20,row*370+332),["A 安靜 / ","B 溫和笑眼 / "][row]+title,font=font,fill="#443d35")
                    # Magnified head is diagnostic nearest-neighbour, not new portrait art.
                    crop=im.crop((52,34,96,69)).resize((220,175),Image.Resampling.NEAREST)
                    heads.paste(crop,(i*260+20,row*270+30),crop)
                    head_draw.text((i*260+18,row*270+218),["A 安靜 / ","B 溫和笑眼 / "][row]+title,font=font,fill="#443d35")
                reports.append({"hairstyle":style,"changed_face_pixels":int(np.any(a!=b,axis=2).sum())})
    for name,digest in original_hashes.items():
        assert hashlib.sha256((ROOT/"combinations"/name).read_bytes()).hexdigest()==digest
    board.save(OUT/"comparison.png");board.save(ROOT/"faces-review.png")
    heads.save(OUT/"faces-closeup.png")
    qa={"status":"needs-visual-review","face_b":"smiling eyes, proposed, not approved",
      "feature_regions":regions,"reference_scale":0.20289855,"canvas":[128,160],
      "approved_originals_untouched":True,"outside_feature_regions_pixel_identical":True,
      "alpha_silhouette_identical":True,"same_palette":True,
      "proposal_images":20,"active_approved_images":10,"changes":reports,
      "limits":["feature patches are view/pose-specific, not a finished universal face layer",
      "only static face B reviewed; generated remaining frames not used as animation",
      "fringe overlap needs visual review for each hairstyle","second full outfit still not authored"]}
    (OUT/"qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    print(json.dumps(qa))
if __name__=="__main__":main()
