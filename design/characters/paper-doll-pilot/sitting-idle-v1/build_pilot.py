"""Finish one generated seated pose; animate existing pixels without texture rerolls."""
from pathlib import Path
import base64,hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
PROJECT=OUT.parents[3]
ASSETS=PROJECT/'assets/characters/traveler'
TIMES=[2100,950,120,950,1500]

def main():
    source=Image.open(OUT/'sitting-source.png').convert('RGBA')
    pixels=np.array(source);pixels[pixels[:,:,3]<32]=0
    # Source registration: 0.1x, not a new bounding-box fit for each frame.
    small=Image.fromarray(pixels).resize((125,125),Image.Resampling.BOX)
    a=np.array(small);a[:,:,3]=np.where(a[:,:,3]>=128,255,0);a[a[:,:,3]==0]=0
    standing=Image.open(PROJECT/'design/characters/paper-doll-pilot/style-refinement-v1/frames/hb-tshirt-jeans.png').convert('RGBA')
    colors=sorted(set(map(tuple,np.array(standing).reshape(-1,4)))-{(0,0,0,0)})
    palette=Image.new('P',(1,1));flat=[v for color in colors for v in color[:3]]
    palette.putpalette((flat+[0]*768)[:768])
    rgb=Image.fromarray(a[:,:,:3]).quantize(palette=palette,dither=Image.Dither.NONE).convert('RGB')
    body=Image.merge('RGBA',(*rgb.split(),Image.fromarray(a[:,:,3])))
    canvas=Image.new('RGBA',(128,160));canvas.alpha_composite(body,(0,44))
    base=np.array(canvas)
    # Keep the exact approved hairstyle and neutral face instead of adopting the
    # generation's slightly different hair/eyes. Pose-specific body remains new.
    base[:95]=0
    head=Image.open(ASSETS/'layers/head/hb.png').convert('RGBA')
    canvas=Image.fromarray(base);canvas.alpha_composite(head,(-14,30));base=np.array(canvas)
    Image.fromarray(base).save(OUT/'master.png')
    enlarged=Image.new('RGBA',(128,160),'#eee7da');enlarged.alpha_composite(Image.fromarray(base))
    enlarged.resize((512,640),Image.Resampling.NEAREST).save(OUT/'master-review.png')
    # An existing approved closed-eye patch, moved with the exact same head.
    closed=np.array(Image.open(OUT.parent/'idle-finished/frames/frame-02.png').convert('RGBA'))
    blink=base.copy()
    for x0,y0,x1,y1 in ((73,56,77,59),(83,55,85,58)):
        blink[y0+30:y1+30,x0-14:x1-14]=closed[y0:y1,x0:x1]
    def breathe(frame):
        result=frame.copy();result[:121]=frame[1:122];return result
    raised=breathe(base);closed_raised=breathe(blink)
    frames=[base,raised,closed_raised,raised.copy(),base.copy()]
    (OUT/'frames').mkdir(exist_ok=True)
    for i,frame in enumerate(frames):Image.fromarray(frame).save(OUT/f'frames/frame-{i:02}.png')
    palette_colors=[tuple(map(int,c[:3])) for c in colors]
    lut={c:i for i,c in enumerate(palette_colors)}
    def gif_frame(frame):
        data=np.full(frame.shape[:2],255,np.uint8)
        for y,x in np.argwhere(frame[:,:,3]>0):data[y,x]=lut[tuple(frame[y,x,:3])]
        image=Image.fromarray(data);image.putpalette((flat+[0]*768)[:768]);image.info['transparency']=255
        return image
    gifs=[gif_frame(f) for f in frames]
    gifs[0].save(OUT/'sitting-idle.gif',save_all=True,append_images=gifs[1:],duration=TIMES,loop=0,transparency=255,disposal=2,optimize=False)
    display=[];contact=Image.new('RGB',(256*5,344),'#eee7da');draw=ImageDraw.Draw(contact)
    for i,frame in enumerate(frames):
        tile=Image.new('RGBA',(128,160),'#eee7da');tile.alpha_composite(Image.fromarray(frame))
        display.append(tile.convert('RGB').resize((384,480),Image.Resampling.NEAREST))
        contact.paste(tile.convert('RGB').resize((256,320),Image.Resampling.NEAREST),(i*256,0))
        draw.text((i*256+12,324),f'{i}: {TIMES[i]}ms',fill='#49443e')
    contact.save(OUT/'contact-sheet.png')
    display[0].save(OUT/'idle-preview.gif',save_all=True,append_images=display[1:],duration=TIMES,loop=0,disposal=2,optimize=False)
    bg=Image.open(OUT/'beach-background.png').convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
    scene=bg.convert('RGBA');shadow=Image.new('RGBA',scene.size);ImageDraw.Draw(shadow).ellipse((597,611,668,624),fill=(68,48,40,45))
    scene.alpha_composite(shadow);scene.alpha_composite(Image.fromarray(base),(570,475));scene.convert('RGB').save(OUT/'beach-preview.png')
    def uri(path):return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
    data={'background':uri(OUT/'beach-background.png'),'frames':[uri(OUT/f'frames/frame-{i:02}.png') for i in range(5)],'durations':TIMES}
    template=Path(__file__).with_name('preview-template.html').read_text(encoding='utf-8')
    (OUT/'preview.html').write_text(template.replace('__DATA__',json.dumps(data)),encoding='utf-8')
    (OUT/'animation.json').write_text(json.dumps({'status':'pending-visual-review','canvas':[128,160],
        'anchor_px':[64,148],'pose':'sit-se','frames':[f'frames/frame-{i:02}.png' for i in range(5)],
        'durations_ms':TIMES,'loop':True,'unique_frames':3,'head_offset':[-14,30],
        'breath_offset':[0,-1],'fixed_region':[0,122,128,160],'sampling':'nearest',
        'source':'sitting-source.png','method':'generated seated body + exact approved head + existing blink pixels',
        'limitations':['single outfit, hairstyle and color only','one-pixel prototype breath, no articulated chest rig','no separate wind simulation','not a sit-down transition','not adopted in standing catalog']},indent=2),encoding='utf-8')
    print(json.dumps({'source':source.size,'canvas':[128,160],'bbox':Image.fromarray(base).getbbox(),'palette_source_colors':len(colors)}))

if __name__=='__main__':main()
