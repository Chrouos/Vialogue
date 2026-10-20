# Vialogue 遊戲畫面風格探索

日期：2026-10-15。

目前已選定第 04 張的混合方向：柔和像素海灘、細緻原創旅人與乾淨介面。第 01 至 03 張保留為探索過程的參考，不代表目前待選方向。

這些靜態示意圖使用內建 image_gen 產生，並非已實作畫面。前三張均使用黃昏、八人海灘與到信狀態，方便比較。實際遊戲仍依使用者當地時間切換日夜。

| 圖片 | 方向 | 觀察 |
|---|---|---|
| [01-watercolor.png](01-watercolor.png) | 水彩繪本 | 溫暖、有紙張質感；環境細節較多 |
| [02-pixel.png](02-pixel.png) | 柔和像素 | 遊戲感明顯，適合角色與表情動畫 |
| [03-soft-illustration.png](03-soft-illustration.png) | 平滑插畫 | 介面乾淨；實際生成較原先極簡方向更豐富 |

使用者後續選擇第 03 張的柔和感與乾淨介面，並提供 RO 像素人物參考。已產生並獲使用者認可的混合方向：[04-soft-pixel-travelers.png](04-soft-pixel-travelers.png)，詳見[方向紀錄](04-soft-pixel-travelers.md)。後續畫面以此為美術方向。

圖內文字、聲音圖示與到信時的等信狀態只作視覺參考，實際互動以主框架為準：收到瓶子後暫停接收其他瓶子，聲音預設關閉。

## 生成提示詞

### 1. watercolor

```text
Use case: ui-mockup. Create ONE landscape 16:9 high quality in-game screenshot concept for Vialogue, a quiet browser game about anonymous message bottles. This is the playable beach waiting screen, NOT a marketing landing page, NOT a collage, no browser or device frame. Scene: a gently elevated wide view across a sandy beach towards calm sea and horizon at late afternoon, generous open water and breathing room. Exactly eight small anonymous human-like travelers spaced naturally across the beach, sitting in little corners, some facing sea, one writing a letter, two gently waving; no usernames, no chat messages, no nameplates. Very small transient smile/heart emotes above only two people. One small recognizable transparent glass message bottle holding folded paper drifting close to shore with a discreet glint, clickable focal point. Restrained game UI: top left small title "Vialogue"; top right "8 人在海邊" and small speaker toggle; bottom center three compact rounded buttons labeled exactly "寫信", "等信中", "收藏", with "等信中" selected; a small nearby status "有瓶子靠岸了". Traditional Chinese typography, crisp legible UI. No huge headings, no score, no currency, no quests, no chat panel, no decorative navigation, no excessive props. Characters occupy a small part of scenery but are clearly readable with simple varied silhouettes and muted clothes. Composition should make it plausible to click on seats, characters, and bottle. Mood: quiet shared presence, gentle curiosity, intimate yet spacious. Style direction A: hand-painted watercolor and colored-pencil storybook illustration, warm off-white paper grain, delicate uneven outlines, desaturated sea-glass turquoise sea, apricot sunset, oatmeal sand, charming little travelers drawn with expressive simple hand-drawn shapes. Tactile, gentle and light, simple scene rather than detailed landscape painting. UI feels like light paper labels. Keep playable spatial clarity.
```

### 2. pixel

```text
Use case: ui-mockup. Create ONE landscape 16:9 high quality in-game screenshot concept for Vialogue, a quiet browser game about anonymous message bottles. This is the playable beach waiting screen, NOT a marketing landing page, NOT a collage, no browser or device frame. Scene: a gently elevated wide view across a sandy beach towards calm sea and horizon at late afternoon, generous open water and breathing room. Exactly eight small anonymous human-like travelers spaced naturally across the beach, sitting in little corners, some facing sea, one writing a letter, two gently waving; no usernames, no chat messages, no nameplates. Very small transient smile/heart emotes above only two people. One small recognizable transparent glass message bottle holding folded paper drifting close to shore with a discreet glint, clickable focal point. Restrained game UI: top left small title "Vialogue"; top right "8 人在海邊" and small speaker toggle; bottom center three compact rounded buttons labeled exactly "寫信", "等信中", "收藏", with "等信中" selected; a small nearby status "有瓶子靠岸了". Traditional Chinese typography, crisp legible UI. No huge headings, no score, no currency, no quests, no chat panel, no decorative navigation, no excessive props. Characters occupy a small part of scenery but are clearly readable with simple varied silhouettes and muted clothes. Composition should make it plausible to click on seats, characters, and bottle. Mood: quiet shared presence, gentle curiosity, intimate yet spacious. Style direction B: sophisticated cozy 2D pixel art game, consistent crisp visible pixel grid, carefully limited palette, seafoam teal waves with pixel foam, muted lavender and peach sunset, sandy rose and beige shore, tiny original expressive pixel travelers with readable sitting poses. Intentionally low resolution art cleanly upscaled with sharp nearest-neighbor pixels; NO blurry pseudo pixels, no painted texture, no 3D. Minimal pixel panel framing while Traditional Chinese UI remains readable. No imitation of any existing game.
```

### 3. minimal

```text
Use case: ui-mockup. Create ONE landscape 16:9 high quality in-game screenshot concept for Vialogue, a quiet browser game about anonymous message bottles. This is the playable beach waiting screen, NOT a marketing landing page, NOT a collage, no browser or device frame. Scene: a gently elevated wide view across a sandy beach towards calm sea and horizon at late afternoon, generous open water and breathing room. Exactly eight small anonymous human-like travelers spaced naturally across the beach, sitting in little corners, some facing sea, one writing a letter, two gently waving; no usernames, no chat messages, no nameplates. Very small transient smile/heart emotes above only two people. One small recognizable transparent glass message bottle holding folded paper drifting close to shore with a discreet glint, clickable focal point. Restrained game UI: top left small title "Vialogue"; top right "8 人在海邊" and small speaker toggle; bottom center three compact rounded buttons labeled exactly "寫信", "等信中", "收藏", with "等信中" selected; a small nearby status "有瓶子靠岸了". Traditional Chinese typography, crisp legible UI. No huge headings, no score, no currency, no quests, no chat panel, no decorative navigation, no excessive props. Characters occupy a small part of scenery but are clearly readable with simple varied silhouettes and muted clothes. Composition should make it plausible to click on seats, characters, and bottle. Mood: quiet shared presence, gentle curiosity, intimate yet spacious. Style direction C: refined minimal 2D vector-like illustration, flat organic shapes, very restrained clean lines, large calm muted blue-green sea and pale sand areas, subtle warm peach sky, almost no texture, no intricate details. Small original rounded faceless characters with simple individual silhouettes, elegant adult-friendly cozy game rather than corporate illustration. Soft restrained shadows only, perfectly clear interactive silhouettes. UI simple translucent ivory pills. Minimal and spacious but still unmistakably a game you can sit inside.
```

