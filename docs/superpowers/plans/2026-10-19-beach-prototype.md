# Beach prototype implementation plan

**Goal:** 在本機實際體驗移動、坐下等信、寫信與接續累積信件。

**Architecture:** `prototype/` 使用無建置流程的 HTML、CSS 與原生 JavaScript。純資料模型與畫面分開，時間可注入測試；狀態與圖片存在 localStorage，沒有伺服器或真實配送。

**Tech Stack:** Browser Canvas、native dialog、Web Audio、localStorage、Node built-in test runner。

**Spec:** 使用者已同意的最小體驗，以及 `VIALOGUE-CONCEPT.md` 的冷卻、收件與返航規則。這是已同意範圍的本機流程試作，不先建立完整多人架構。

## Constraints

- 沿用已確認站姿與坐姿素材，保留原檔；移動先用站姿位移代替尚未完成的走路影格。
- 示例旅人與信件明確標示，不虛構真人回信、帳號或寄送成功。
- 無固定到信保證；另提供明確的試玩工具讓示例瓶靠岸。
- 新瓶冷卻 30 分鐘；未拆 3 分鐘、已拆閒置 30 分鐘；5 封或漂流滿 7 天返航，手上跨 7 天可寫完。
- 文字最多 500 字、一張圖片；上傳僅供本機試玩，暫限 JPEG/PNG/WebP 5 MB 並縮小保存。
- 不部署、不連接 Google、不建立多人房間。原始體驗規格仍是正式版本依據。

## Tasks

- [x] `prototype/model.test.cjs` 先測冷卻、坐姿資格、三分鐘逾時、操作續期、五封／七天返航及去重，再建立 `prototype/model.js`。9 項通過。
- [x] `prototype/index.html`、`style.css`、`app.js`：全景海灘、點選移動與坐下、匿名示例旅人、待機影格、寫信／圖片、閱讀／接續、旅途與收藏、草稿、聲音。
- [x] `prototype/check-browser.cjs`：19 項流程檢查通過，包含圖片處理與跨分頁保存邊界，擷取已檢視。
- [x] 更新 README、啟動入口與現況紀錄，說明示例資料、走路影格與正式連線的限制。

## Review record

獨立程式審查發現跨分頁覆寫與圖片處理競態，已以 Web Locks 與圖片處理狀態／token 修正，新增對應瀏覽器檢查。複核未發現未解的實質缺陷。本機試玩未部署。

在目前共用工作區直接實作；此目錄尚非 Git repository，不建立空的 worktree 或擅自初始化 Git。
