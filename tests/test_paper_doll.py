import json
import tempfile
import unittest
import numpy as np
from pathlib import Path
from PIL import Image
from tools.paper_doll import compose, load_catalog, build_preview


class LayerContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        Image.new('RGBA',(4,4),(200,100,50,255)).save(self.root/'body.png')
        Image.new('RGBA',(1,1),(0,120,255,255)).save(self.root/'hat.png')
        self.data={'schema':'vialogue.paper-doll.v1','canvas':{'width':4,'height':4,'anchor':[2,4]},'pose':'stand-se','slots':[
            {'id':'outfit','label':'衣服','z':20,'required':True,'default':'base','variants':[{'id':'base','label':'基本','file':'body.png'}]},
            {'id':'hat','label':'帽子','z':60,'required':False,'default':None,'variants':[{'id':'blue','label':'藍帽','file':'hat.png','offset':[1,0]}]}
        ]}
        self.path=self.root/'catalog.json'

    def catalog(self):
        self.path.write_text(json.dumps(self.data),encoding='utf-8')
        return load_catalog(self.path)

    def test_new_optional_slot_offset_and_z_need_no_renderer_change(self):
        self.data['slots'].reverse()  # Rendering follows z, not JSON list order.
        cat=self.catalog()
        plain=compose(cat,{})
        dressed=compose(cat,{'hat':'blue'})
        self.assertEqual(plain.getpixel((1,0)),(200,100,50,255))
        self.assertEqual(dressed.getpixel((1,0)),(0,120,255,255))
        self.assertEqual(dressed.getpixel((0,0)),plain.getpixel((0,0)))
        self.assertEqual(compose(cat,{'hat':None}).tobytes(),plain.tobytes())

    def test_unknown_selections_fail_instead_of_silently_ignoring_them(self):
        cat=self.catalog()
        for selection in ({'typo':'blue'},{'hat':'missing'},{'outfit':None}):
            with self.subTest(selection=selection),self.assertRaises(ValueError):
                compose(cat,selection)

    def test_duplicates_and_missing_assets_are_rejected(self):
        self.data['slots'][1]['id']='outfit'
        with self.assertRaises(ValueError):self.catalog()
        self.data['slots'][1]['id']='hat'
        (self.root/'hat.png').unlink()
        with self.assertRaises(ValueError):self.catalog()

    def test_preview_is_portable_and_contains_all_added_slots(self):
        cat=self.catalog();dest=self.root/'preview.html'
        build_preview(cat,dest)
        html=dest.read_text(encoding='utf-8')
        self.assertIn('data:image/png;base64,',html)
        self.assertIn('帽子',html)
        self.assertNotIn('fetch(',html)

    def test_optional_layer_opacity_composes_with_existing_body(self):
        self.data['slots'][1]['variants'][0]['opacity']=0.5
        image=compose(self.catalog(),{'hat':'blue'})
        self.assertEqual(image.getpixel((1,0)),(100,110,153,255))


class AcceptedArtworkRegressionTests(unittest.TestCase):
    def test_all_hair_colors_preserve_alpha_and_pixels_outside_hair_masks(self):
        assets=Path(__file__).resolve().parents[1]/'assets/characters/traveler'
        cat=load_catalog(assets/'catalog.json')
        head=next(s for s in cat['slots'] if s['id']=='head')
        self.assertEqual(len(head['variants']),25)
        choices=set()
        for variant in head['variants']:
            style=variant['selection']['hairstyle'];color=variant['selection']['color']
            choices.add((style,color))
            source=np.array(Image.open(assets/f'layers/head/{style}.png').convert('RGBA'))
            actual=np.array(Image.open(assets/variant['file']).convert('RGBA'))
            mask=np.array(Image.open(assets/f'masks/hair/{style}.png'))>0
            with self.subTest(variant=variant['id']):
                self.assertTrue(np.array_equal(actual[:,:,3],source[:,:,3]))
                self.assertTrue(np.array_equal(actual[~mask],source[~mask]))
                self.assertTrue(np.array_equal(actual[56:59,73:77],source[56:59,73:77]))
                self.assertTrue(np.array_equal(actual[60:65,71:],source[60:65,71:]))
                self.assertGreater(int(mask.sum()),400)
                if color!='coffee':self.assertTrue(np.any(actual[mask]!=source[mask]))
        self.assertEqual(len(choices),25)

    def test_all15_layer_compositions_match_accepted_static_art(self):
        root=Path(__file__).resolve().parents[1]
        cat=load_catalog(root/'assets/characters/traveler/catalog.json')
        sources=root/'design/characters/paper-doll-pilot/style-refinement-v1/frames'
        for hair in ('ha','hb','hc','hd','he'):
            for outfit in ('tshirt-jeans','cardigan-straight','jacket-shorts'):
                with self.subTest(hair=hair,outfit=outfit):
                    result=compose(cat,{'head':hair,'outfit':outfit})
                    with Image.open(sources/f'{hair}-{outfit}.png') as image:expected=image.convert('RGBA')
                    self.assertEqual(result.size,(128,160))
                    self.assertEqual(result.tobytes(),expected.tobytes())

    def test_browser_rendered_pngs_match_compositor_when_captured(self):
        root=Path(__file__).resolve().parents[1]
        assets=root/'assets/characters/traveler'
        frames=assets/'qa/ui-frames'
        if not frames.exists():self.skipTest('Run optional headless browser capture first')
        cat=load_catalog(assets/'catalog.json')
        heads=next(s for s in cat['slots'] if s['id']=='head')['variants']
        outfits=next(s for s in cat['slots'] if s['id']=='outfit')['variants']
        self.assertEqual(len(list(frames.glob('*.png'))),len(heads)*len(outfits))
        for head in heads:
            hair=head['id']
            for item in outfits:
                outfit=item['id']
                with self.subTest(hair=hair,outfit=outfit):
                    expected=compose(cat,{'head':hair,'outfit':outfit})
                    with Image.open(frames/f'{hair}-{outfit}.png') as image:actual=image.convert('RGBA')
                    self.assertEqual(actual.tobytes(),expected.tobytes())


if __name__=='__main__':unittest.main()
