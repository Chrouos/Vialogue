"""Verify the exported PNG/GIF, fixed ground contact, and single-master motion."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label
OUT=Path(__file__).resolve().parent

def main():
    metadata=json.loads((OUT/'animation.json').read_text(encoding='utf-8'))
    frames=[np.array(Image.open(OUT/f).convert('RGBA')) for f in metadata['frames']]
    base,raised,blink,_,_=frames
    assert len(frames)==5 and len({f.tobytes() for f in frames})==3
    assert all(f.shape==(160,128,4) for f in frames)
    assert all(set(np.unique(f[:,:,3]))<={0,255} for f in frames)
    assert all(np.array_equal(f[122:],base[122:]) for f in frames)
    assert all(np.array_equal(f[130:148,30:47],base[130:148,30:47]) for f in frames)
    assert np.array_equal(raised[:121],base[1:122])
    assert np.array_equal(base,frames[-1])
    eye=np.zeros(base.shape[:2],bool);eye[85:88,59:63]=True;eye[84:87,69:71]=True
    assert np.array_equal(blink[~eye],raised[~eye])
    assert np.any(blink[eye]!=raised[eye])
    components=[]
    for frame in frames:
        labels,count=label(frame[:,:,3]>0)
        sizes=np.bincount(labels.ravel())[1:];components.append(int(count))
        assert sizes.max()/sizes.sum()>.995
    gif=Image.open(OUT/'sitting-idle.gif');assert gif.n_frames==5
    times=[]
    for i,frame in enumerate(frames):
        gif.seek(i);times.append(gif.info['duration']);actual=np.array(gif.convert('RGBA'))
        assert np.array_equal(actual[:,:,3],frame[:,:,3])
        visible=frame[:,:,3]>0;assert np.array_equal(actual[visible],frame[visible])
    assert times==metadata['durations_ms']
    browser=OUT/'browser-check.json'
    if browser.exists():
        checks=json.loads(browser.read_text(encoding='utf-8'));assert checks['frames_captured']==5 and not checks['mobile_overflow']
        for i,frame in enumerate(frames):
            actual=np.array(Image.open(OUT/f'browser-frame-{i}.png').convert('RGBA'))
            visible=frame[:,:,3]>0
            assert np.array_equal(actual[:,:,3],frame[:,:,3])
            assert np.array_equal(actual[visible],frame[visible])
    result={'structural_checks_passed':True,'visual_approval':'pending','gif_frames':5,'unique_frames':3,
        'durations_ms':times,'fixed_ground_and_supporting_hand':True,'texture_drift_after_known_translation':0,
        'blink_changes_confined_to_eye_patches':True,'gif_matches_png_pixels':True,'connected_components':components,
        'browser_frames_matched':5 if browser.exists() else None,
        'scope':'one seated outfit only; not sitting-down transition or general animated paper doll'}
    (OUT/'qa.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))

if __name__=='__main__':main()
