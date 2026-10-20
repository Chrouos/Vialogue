# 紙娃娃與逐格動畫試作

後續新增素材與圖層，統一由 [CHARACTER-ASSETS.md](../../../CHARACTER-ASSETS.md) 進入；設定與 PNG 在 assets/characters/traveler，歷史試稿仍保留於此。

更新日期：2026-10-19。

## 目前採用的方向

使用者認可 master-source.png 的人物及 idle-finished 待機影格的像素感。最初獨立生成部位所疊成的八種換裝組合被拒絕，比例校正 standing-v2 也不視為正式造型。

目前直接使用已認可的 idle-finished 影格驗證換裝，不重新縮製整個人物或拼接舊部位。[短偏分](hair-b-v1/README.md)、[固定像素待機](stable-idle-v1/README.md)及[後梳、微捲短髮與低束小髮髻](mens-hair-options-v2/README.md)均已獲認可。包含原始髮型共五款，已加入十張靜態組合。上一輪微分碎蓋與斜瀏海的畫法已被拒絕，canonical-v3 已停用。

## 目前可看

- [最新審美修訂](style-refinement-v1/README.md)：新版五款髮型已獲確認，後梳與微捲輪廓分開、改善瀏海與眼周間隙；第三套輕薄外套待確認，提供衣服與外套前後對照。未來五種髮色已記錄於 [規格](planned-hair-colors.json)，目前仍為咖啡色。

- [5 髮型 × 3 套衣服的 15 種搭配驗證](outfit-hair-validation-v1/README.md)：一般表情站姿，領口與肩膀保留各套新衣物，身體與腳底位置一致；尚未驗證其他七款表情或動作。

- [已確認的三套現代日常穿搭 v2](modern-outfits-v2/README.md)：T-shirt＋牛仔褲、針織外套＋直筒褲、短外套＋短褲。沿用短偏分與一般表情，尚未分層或製作動畫。

- [目前暫用的八款表情 v4](expression-runtime-v4/README.md)：一般、開心、超開心、為難、傷心、超傷心、害羞、生氣。使用者已確認先用這版，後續改善見[專案 TODO](../../../TODO.md)。目前僅短偏分靜態版本，尚未整合動畫或其他髮型。
- [換裝對照圖](combinations-review.png)：五種髮型各搭配綠藍背心，共十種。
- [目前換裝圖片](combinations)：髮型 B 只替換頭髮周圍，保護原五官與全身；同髮型兩種背心的頭部完全相同。
- [髮型 B 待機 GIF](hair-b-v1/idle-preview.gif)。
- [待機 GIF](idle-preview.gif)：4 張 PNG 組成，不使用影片。
- [待機影格](idle-finished/frames)：128 × 160 透明 PNG，人物高 112 像素。
- [待機時間與封裝](idle-clips/animation-clips.json)：1600、350、140、450 毫秒，總長 2540 毫秒。

綠、藍背心是同一件衣服的舊配色測試。目前採用五款髮型、三套已確認現代穿搭與暫用 v4 八款表情；已驗證一般表情的 15 種髮型穿搭組合，尚未完成所有表情與動作、方向通用的紙娃娃分層。

## 檔案狀態

- master-source.png、master：共用人物的來源與 Forge 處理資訊。
- idle-base-v4：目前站姿換裝驗證、圖層與逐像素檢查。
- hair-b-v1：最新髮型 B、4 格動態、對照圖及一致性檢查。
- canonical-v3：已停用的重新縮製試作，保留來源與提示詞，不作為目前基準。
- idle-finished、idle-clips、idle-preview.gif：使用者認可畫風的待機素材，仍需動作修整。
- archive/rejected-initial-combinations：原始八張被拒絕的換裝圖，只供追溯。
- standing-v2、parts-source.png、parts-keyed、layers-standing、paper-doll.json：歷史試作，不作為目前可用的紙娃娃素材。
- build_pilot.py prepare 已停用，避免重新覆寫目前 combinations；gif 功能仍可重建原待機預覽。

## 工具與檢查

已安裝 [Agent Sprite Forge](https://github.com/0x0funky/agent-sprite-forge) 五個 skills。使用內建 ImageGen 產生及編輯圖像，Forge 工具去背、切格、縮放、像素處理與封裝，Python 組成 GIF。route 為 host-image_gen，未取得可核實的模型名稱與費用。未用影片生成。

目前換裝驗證檢查：頭臉一致、輪廓一致、服裝以外像素一致、分層重組完全相同。新的像素處理 warnings 為空，狀態仍是 needs-visual-review。這些數值不代表新換裝已獲使用者核准。

原待機素材每格最多 30 色、透明度為二值，4 格及 GIF 時間均已解碼驗證。原始人物影格間仍有細節跳動，尚未完成逐格修整。歷史 parts 切格曾發現跨格 2 像素，改用 ownership 切割處理；該批 parts 不再採用。

## 下一步

以共用基準圖與待機造型逐一製作、確認髮型及臉的替換，再擴充完整穿搭；先確保站姿一致，再做待機分層、坐姿與走路，最後補齊已定款式。保留透明 PNG 為原始素材，GIF 作為動態預覽。
