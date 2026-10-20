# 紙娃娃設定畫面 v2

日期：2026-10-15。

[畫面](character-customization-v2.png)使用內建 ImageGen 編輯 v1 產生。使用者認可 v1 的設定畫面，要求海灘、人物與整體更平滑、更有像素感；此版本待確認。

保留原版面、色調與控制項，減少細碎紋理，改用更明顯、連貫的像素色塊與輪廓，UI 文字維持清楚。角色縮圖仍有少量髮色不一致，正式版需依目前所選髮色統一顯示。此圖為靜態示意，尚非模組化角色或動畫素材。

## 完整提示詞

```text
Edit the provided Vialogue character customization mockup. This is a targeted ART STYLE REFINEMENT. Preserve its exact overall UI layout, ivory panel, warm muted sunset colors, all Traditional Chinese labels, same controls, counts (6 hairstyles, 6 swatches, 4 faces, 6 outfits), selected outfit identity, main character and seated/walking preview poses. Do not redesign the interface.

User request: beach background, characters, and overall artwork should feel smoother, cleaner, and MORE clearly pixel-art. Interpret smoother as well-designed cohesive PIXEL CLUSTERS and calm shading, NOT blur. The original is too finely illustrated and noisy, with hair strand detail and many tiny textured highlights. Make a visibly different, cleaner pixel art pass:
1. All environment artwork: render on a deliberately lower-resolution consistent pixel grid (roughly 480x270 base scene scaled to the wide canvas), with visible crisp square pixels, clean stair-step contours and very sparse detail. Use large unified sea color regions, a few rhythmic wave lines, simplified clean rock silhouettes and smooth quiet sky color bands. Eliminate dense tiny sea sparkle, stippled sand, pebble noise and painterly brush texture. Soft harmonious colors, controlled 3-4 shade clusters per material. No Gaussian blur, no mottled texture, no pixelation filter applied to unchanged painting.
2. All character artwork including thumbnails and alternate poses: recognizable high-quality original 2D MMORPG-like pixel sprites with oversized friendly heads and compact body proportions, actual designed pixel shapes and clean continuous dark pixel outlines. Main standing sprite should LOOK like an original approx 80-100 pixel tall sprite enlarged cleanly 4x, rather than high resolution anime illustration with pixel edges. Simplify hair into 4-6 flowing pixel clusters, clothes into readable light/mid/shadow masses, crisp eyes and compact faces. Restrained material shading. Preserve brown hair, cream shirt, sage scarf, brown trousers, satchel, boots. No individual fine hair strands, no scratchy linework, no microhighlights. Sitting and walking previews MUST be same character and outfit.
3. Keep interface text and framing clean high-resolution and readable; do not force pixelation on UI text. Entire aesthetic polished, calm, smooth-shaded intentional pixel art rather than rough grain or busy illustrated landscape. Strong perceptible reduction in texture/detail while maintaining warmth and charm.
4. Hairstyle thumbnails use the currently selected brown hair color consistently (different silhouettes, NOT different colors); hair color swatches handle color separately.
Avoid new props, new features, added text, ornamental clutter, shiny 3D rendering, soft-focus sprites, watercolor, realistic humans. Output one full landscape screenshot, no collage or comparison labels.
```

