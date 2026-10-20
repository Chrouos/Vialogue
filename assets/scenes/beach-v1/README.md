# 海灘場景 v1

1280 × 720 分層場景；新增美術由內建 ImageGen 生成，尚待使用者檢視。原角色 PNG 與 catalog 沿用，沒有改動角色美術基準。

- `sources/neutral-beach-v1.png`：中性白天原圖；提示保留於 neutral-prompt.txt。
- `sources/beach-fx-atlas-v1.png`：透明 FX 原圖，4 × 4 分格；提示保留於 fx-prompt.txt。
- `layers/`：同一原圖等比 nearest 縮放至世界尺寸，再依遮罩分出天空、海面與地面，RGB 保留；sky-mask 的 alpha 與天空相同。
- `effects/`：依 atlas 分格裁切及 alpha 邊界整理，包含表情、工具、雲、日月與三格海鷗。沒有用程式重畫場景美術。
- `provenance.json`：原圖 SHA-256、處理方式、Pixi 來源與官方 hash。
- `scene.json`：貼圖、比例、錨點、岸線、沙畫區與旅人位置入口。
- `map-bundle.json`：可走區、角色半徑、出生點與互動目標；幾何供畫面與導航共用。

```powershell
python tools/build_beach_scene.py
python -m unittest discover -s tests -p test_beach_scene.py -v
node --test prototype/navigation.test.cjs
```

打包工具讀取 scene.json、圖片與地圖，建立可直接 file 開啟的 prototype/scene-pack.js；本地 PixiJS 8.20.1 的 MIT 授權在 prototype/vendor。請保留原圖與提示，更新圖像或錨點時重建 pack 並重新檢查。

`qa/bundle-v3.json` 為地圖結構結果；`qa/nav-v2/` 為可達性結果。`qa/preview-v2/preview.html` 是獨立可玩地圖預覽；Playwright 未安裝，改以隔離 Chrome/CDP 呼叫真實預覽 traverseAll，結果在 prototype/qa/living-beach/map-routes.json。動態場景與介面畫面在 prototype/qa/living-beach。
