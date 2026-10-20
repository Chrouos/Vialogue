import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class ScenePackTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / 'tools/build_beach_scene.py').exists(), 'scene pack builder is missing')
        spec = importlib.util.spec_from_file_location('beach_builder', ROOT / 'tools/build_beach_scene.py')
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        Image.new('RGBA', (2, 2), (12, 24, 36, 0)).save(self.folder / 'sky.png')
        self.scene = {'version': 1, 'world': {'width': 1280, 'height': 720}, 'map': 'map.json',
                      'textures': {'sky': {'file': 'sky.png', 'anchor': [0, 0], 'scale': 1}}, 'config': {}}
        (self.folder / 'map.json').write_text(json.dumps({'world': self.scene['world']}), encoding='utf-8')

    def build(self):
        path = self.folder / 'scene.json'
        path.write_text(json.dumps(self.scene), encoding='utf-8')
        return self.builder.build_scene(path, self.folder / 'pack.js')

    def test_pack_embeds_real_png_and_source_dimensions(self):
        result = self.build()
        packed = (self.folder / 'pack.js').read_text(encoding='utf-8')
        data = json.loads(packed.split('=', 1)[1].strip().removesuffix(';'))
        self.assertEqual(data['textures']['sky']['width'], 2)
        self.assertTrue(data['textures']['sky']['src'].startswith('data:image/png;base64,'))
        self.assertEqual(result['textures'], 1)

    def test_missing_texture_is_rejected(self):
        self.scene['textures']['sky']['file'] = 'missing.png'
        with self.assertRaises(FileNotFoundError):
            self.build()

    def test_wrong_hash_and_anchor_are_rejected(self):
        self.scene['textures']['sky']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.build()
        del self.scene['textures']['sky']['sha256']
        self.scene['textures']['sky']['anchor'] = [3, 0]
        with self.assertRaisesRegex(ValueError, 'anchor'):
            self.build()
