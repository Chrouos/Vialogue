"""Build the offline scene pack without changing source artwork."""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from PIL import Image


def build_scene(scene_path: Path, out_path: Path) -> dict:
    scene_path, out_path = Path(scene_path), Path(out_path)
    scene = json.loads(scene_path.read_text(encoding='utf-8'))
    textures = {}
    for key, item in scene['textures'].items():
        path = (scene_path.parent / item['file']).resolve()
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if item.get('sha256', digest) != digest:
            raise ValueError(f'hash mismatch: {key}')
        with Image.open(path) as image:
            width, height = image.size
            anchor = item.get('anchor', [0, 0])
            if len(anchor) != 2 or not (0 <= anchor[0] <= width and 0 <= anchor[1] <= height):
                raise ValueError(f'invalid anchor: {key}')
            if item.get('scale', 1) <= 0:
                raise ValueError(f'invalid scale: {key}')
            textures[key] = {**item, 'src': 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii'),
                             'width': width, 'height': height, 'anchor': anchor, 'sha256': digest}
    data = {'version': 1, 'world': scene['world'], 'map': json.loads((scene_path.parent / scene['map']).read_text(encoding='utf-8')),
            'config': scene.get('config', {}), 'textures': textures}
    output = 'globalThis.VialogueScenePack=' + json.dumps(data, ensure_ascii=True, separators=(',', ':')) + ';\n'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding='utf-8')
    return {'textures': len(textures), 'bytes': len(output.encode('utf-8')), 'sha256': hashlib.sha256(output.encode('utf-8')).hexdigest()}


def build_runtime(source: Path, target: Path):
    text = source.read_text(encoding='utf-8')
    names = re.findall(r'^export (?:const|function) (\w+)', text, flags=re.M)
    body = re.sub(r'^export ', '', text, flags=re.M)
    wrapper = "(function(r,f){if(typeof module==='object'&&module.exports)module.exports=f();else r.VialogueMapRuntime=f();})(globalThis,()=>{\n"
    target.write_text(wrapper + body + '\nreturn {' + ','.join(names) + '};\n});\n', encoding='utf-8')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', type=Path, default=root / 'assets/scenes/beach-v1/scene.json')
    parser.add_argument('--out', type=Path, default=root / 'prototype/scene-pack.js')
    args = parser.parse_args()
    build_runtime(root / 'prototype/vendor/map-runtime.mjs', root / 'prototype/vendor/map-runtime.js')
    print(json.dumps(build_scene(args.scene, args.out)))
