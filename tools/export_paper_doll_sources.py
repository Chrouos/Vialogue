"""Export the accepted fixed-pose source art into the initial layer kit.

Re-exports stock head/outfit PNGs only. Does not overwrite catalog.json or
user-added variants. Invoke deliberately when refreshing accepted sources.
"""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'design/characters/paper-doll-pilot/style-refinement-v1'
DEST=ROOT/'assets/characters/traveler'

def main():
    provenance=[]
    for hair in ('ha','hb','hc','hd','he'):
        path=SOURCE/'heads'/f'{hair}.png'
        source=Image.open(path).convert('RGBA');out=Image.new('RGBA',(128,160))
        out.alpha_composite(source.crop((0,0,128,65)),(0,0))
        dest=DEST/'layers/head'/f'{hair}.png';dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
        provenance.append({'file':str(dest.relative_to(DEST)).replace('\\','/'),'source':str(path.relative_to(ROOT)).replace('\\','/'),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'combined head, rows0..64'})
    for oid in ('tshirt-jeans','cardigan-straight','jacket-shorts'):
        path=SOURCE/'frames'/f'hb-{oid}.png'
        source=Image.open(path).convert('RGBA');out=Image.new('RGBA',(128,160))
        out.alpha_composite(source.crop((0,65,128,160)),(0,65))
        dest=DEST/'layers/outfit'/f'{oid}.png';dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
        provenance.append({'file':str(dest.relative_to(DEST)).replace('\\','/'),'source':str(path.relative_to(ROOT)).replace('\\','/'),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'combined body and outfit, rows65..159'})
    (DEST/'provenance.json').write_text(json.dumps({'art_source':'existing approved ImageGen art','exports':provenance,'fine_layers_complete':False},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Exported 5 head and 3 outfit layers; catalog and custom layers left unchanged.')

if __name__=='__main__':main()
