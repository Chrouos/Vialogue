"""Data-driven static paper-doll compositor. Art is supplied as PNG layers."""
from pathlib import Path
import argparse,base64,json,re
from PIL import Image

PROJECT=Path(__file__).resolve().parents[1]
DEFAULT_CATALOG=PROJECT/'assets/characters/traveler/catalog.json'
ID=re.compile(r'^[a-z][a-z0-9_-]*$')

def load_catalog(path):
    path=Path(path).resolve()
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema')!='vialogue.paper-doll.v1':raise ValueError('Unsupported catalog schema')
    canvas=data.get('canvas',{})
    if any(type(canvas.get(k)) is not int or canvas[k]<=0 for k in ('width','height')):
        raise ValueError('Canvas width/height must be positive integers')
    slots=data.get('slots',[]);seen=set()
    for slot in slots:
        sid=slot.get('id','')
        if not ID.fullmatch(sid) or sid in seen:raise ValueError(f'Invalid/duplicate slot: {sid}')
        seen.add(sid)
        if type(slot.get('z')) is not int:raise ValueError(f'Slot {sid}: integer z required')
        variants=slot.get('variants',[]);ids=set()
        for variant in variants:
            vid=variant.get('id','')
            if not ID.fullmatch(vid) or vid in ids:raise ValueError(f'Slot {sid}: invalid/duplicate variant {vid}')
            ids.add(vid)
            asset=(path.parent/variant['file']).resolve()
            if not asset.is_file():raise ValueError(f'Missing asset: {variant["file"]}')
            with Image.open(asset) as im:
                if im.format!='PNG':raise ValueError(f'PNG required: {asset}')
                im.verify()
            offset=variant.get('offset',[0,0])
            if len(offset)!=2 or any(type(n) is not int for n in offset):raise ValueError('offset must be [integer, integer]')
            opacity=variant.get('opacity',1)
            if not isinstance(opacity,(int,float)) or not 0<=opacity<=1:raise ValueError('opacity must be 0..1')
        default=slot.get('default')
        if default is not None and default not in ids:raise ValueError(f'Unknown default in slot {sid}')
        if slot.get('required',False) and default is None:raise ValueError(f'Required slot {sid} needs a default')
    data['_root']=path.parent;data['_path']=path
    return data

def selected_layers(catalog,selection):
    known={s['id'] for s in catalog['slots']}
    unknown=set(selection)-known
    if unknown:raise ValueError(f'Unknown slot(s): {sorted(unknown)}')
    result=[]
    for slot in sorted(catalog['slots'],key=lambda s:s['z']):
        chosen=selection.get(slot['id'],slot.get('default'))
        if chosen is None:
            if slot.get('required',False):raise ValueError(f'Cannot disable required slot: {slot["id"]}')
            continue
        variant=next((v for v in slot['variants'] if v['id']==chosen),None)
        if variant is None:raise ValueError(f'Unknown variant {chosen!r} in slot {slot["id"]}')
        result.append((slot,variant))
    return result

def compose(catalog,selection=None):
    canvas=catalog['canvas'];image=Image.new('RGBA',(canvas['width'],canvas['height']))
    for slot,variant in selected_layers(catalog,selection or {}):
        with Image.open(catalog['_root']/variant['file']) as source:layer=source.convert('RGBA')
        opacity=variant.get('opacity',1)
        if opacity!=1:layer.putalpha(layer.getchannel('A').point(lambda a:round(a*opacity)))
        image.alpha_composite(layer,tuple(variant.get('offset',[0,0])))
    return image

def build_preview(catalog,destination):
    data={k:v for k,v in catalog.items() if not k.startswith('_')}
    # Deep-copy: preview metadata must not mutate the runtime catalog.
    data=json.loads(json.dumps(data))
    for slot in data['slots']:
        for variant in slot['variants']:
            asset=catalog['_root']/variant['file']
            variant['_src']='data:image/png;base64,'+base64.b64encode(asset.read_bytes()).decode('ascii')
    encoded=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    template=Path(__file__).with_name('paper_doll_preview.html').read_text(encoding='utf-8')
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(template.replace('__CATALOG_JSON__',encoded),encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',type=Path,default=DEFAULT_CATALOG)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('validate')
    render=sub.add_parser('render');render.add_argument('--pick',action='append',default=[]);render.add_argument('--out',type=Path,required=True)
    preview=sub.add_parser('preview');preview.add_argument('--out',type=Path)
    args=parser.parse_args()
    try:
        catalog=load_catalog(args.catalog)
        if args.command=='validate':
            compose(catalog)
            print(json.dumps({'valid':True,'slots':len(catalog['slots']),'variants':sum(len(s['variants']) for s in catalog['slots']),'pose':catalog.get('pose')},ensure_ascii=False))
        elif args.command=='preview':
            dest=args.out or catalog['_root']/'preview.html';build_preview(catalog,dest);print(dest)
        else:
            picks={}
            for pair in args.pick:
                if '=' not in pair:raise ValueError('--pick must be slot=variant or slot=none')
                key,value=pair.split('=',1);picks[key]=None if value=='none' else value
            image=compose(catalog,picks);args.out.parent.mkdir(parents=True,exist_ok=True);image.save(args.out);print(args.out)
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as exc:
        parser.exit(1,f'error: {exc}\n')

if __name__=='__main__':main()
