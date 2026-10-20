# 海邊漂流瓶：本機核心試玩

[開始試玩](index.html)。此版本沒有部署或連接外部服務，可直接用新版 Chrome／Edge 開啟 HTML。

## 怎麼玩

1. 點前方平坦沙地，角色慢慢移動，到位置後坐下。自己的腳下有淡淡標記。鍵盤也可用方向鍵與空白鍵操作。
2. 選「寫一封信」，可寫 1～500 字、夾一張照片，再放進本機旅途。新瓶子的冷卻為 30 分鐘，期間仍能寫私人草稿。
3. 坐著並開啟等信，才有機會收到示例瓶。也可在「試玩工具」明確操作立即靠岸，不必為了測流程等待。
4. 從第一封依序翻閱，選擇添信或讓它繼續漂。添信不受新瓶子冷卻限制。
5. 「我的旅途」保留漂流狀態、返航內容、收藏與草稿。工具可將試玩時間推進 30 分鐘或 7 天。
6. 「草稿」可直接繼續寫新信或接續仍持有的瓶子。瓶子已離開時，可取回私人草稿、複製文字及查看保留照片，無法補入原瓶，也不會覆蓋其他草稿。
7. 瓶子返航後，海灘顯示「閱讀完整旅途」。提醒會保留到開啟該瓶，重新載入也不會消失；讀過的內容仍能從「歸來的瓶子」重看及收藏。

## 已實作的規則

- 只有坐下且開啟等信才會配送，一次一瓶；示例配送採隨機嘗試，沒有固定到信保證。
- 未拆 3 分鐘離開；已拆後閒置 30 分鐘離開。閱讀翻頁、寫字等實際操作補回時間，重開頁面與單純停留不補時。
- 新瓶冷卻、持瓶期限與草稿會保留；離線時間也會計入。依本機時鐘計算，非正式伺服器時間。
- 已讀放回或寫過的瓶子不再配送。沒有拆開就錯過的示例可再次遇到。
- 加到第五封立即返航；漂流滿七天返航。人手上的瓶子跨七天可繼續操作，直到送出、放回或閒置逾時才返航。
- 沒有人添信的瓶子會原封返航，不生成假回信或假拾取紀錄。
- 照片暫限 5 MB 以內 JPEG／PNG／WebP，縮到長邊 1280 px 內，以 JPEG 存入本機。圖片處理時阻擋送出，避免漏圖。
- 海浪白噪音預設關閉，由聲音按鈕開啟；開啟後到信會有輕提示音。
- 以 Web Locks 保護本機紀錄，同一來源一次只有一個分頁能操作；第二分頁不會覆寫信件或冷卻。

## 試玩與正式遊戲的差別

- 海邊四位其他旅人是示例角色；三組預寫信件是體驗素材，並非真人寄件。介面、初次說明與示例信抬頭都有標示。
- 寄出與接續只變更本機紀錄，不會發送給別人。沒有 Google 登入、真實房間、跨裝置資料或配送伺服器。
- 移動先用已確認站姿的位移與輕微起伏模擬，尚非完整走路影格；也沒有站立轉坐下的過程。
- 已接入本機時間日夜、雲、浪花、海鷗、頭頂表情與短暫沙畫；通知權限與檢舉尚未接入。
- 玩家固定為短偏分／咖啡色／T-shirt＋牛仔褲。換裝素材入口仍獨立保留，不在此輪擴充所有坐姿造型。
- 資料只留在此瀏覽器來源，清除瀏覽器資料即會清除紀錄。直接開檔與 HTTP 開啟是不同來源，不共享紀錄。

## 開發與驗證

遊玩無需安裝或建置。PixiJS 8.20.1 與地圖 runtime 已存於本地 vendor，授權與來源隨附。`model.js` 管理純資料規則，`app.js` 串接操作、保存、圖片及聲音，`scene.js` 管理 Pixi 呈現，`environment.js`／`interactions.js` 管理場景與互動，`style.css` 管理桌面與直向手機版。沿用 `assets/characters/traveler/` 與 `design/characters/paper-doll-pilot/sitting-idle-v1/` 原有美術。

```powershell
node --test prototype/model.test.cjs
node --check prototype/app.js
```

9 項規則測試涵蓋冷卻、坐姿資格、重複配送、逾時、操作續期、返航與草稿。另以隔離 Chrome 驗證圖片處理、兩個分頁、重新載入、翻信接續、草稿續寫與過期取回、剪貼簿複製、返航閱讀入口、收藏、時間推進與手機版。最新檢查項目及結果在 [qa](qa/browser-check.json)。

瀏覽器檢查腳本 `check-browser.cjs` 使用獨立 Chrome 的 `127.0.0.1:9347`，不連接使用者現有瀏覽器。以 `node prototype/run-existing-checks.cjs` 重跑，runner 自行建立並核對隔離 profile；結束只關閉自己的測試瀏覽器。

如需用本機 HTTP 測試，可在專案根目錄執行 `python -m http.server 4173 --bind 127.0.0.1`，再開啟 `http://127.0.0.1:4173/`；這不會部署網站。

## 會動的海灘

海浪約每 7～12 秒往返，海鷗偶爾經過；日夜跟隨本機時間。試玩工具可以切換場景時段或加速日夜，這與瓶子冷卻／七天返航的時間推進分開。

點頭頂或「表情」，也可按 E，選揮手、開心、驚訝或陪伴。附近的示例旅人可能回應。文字輸入時 E 照常打字。

「畫沙」讓角色停下，暫停等信。可在身旁沙地拖曳作畫；濕沙痕被經過的浪逐段淡去，乾沙約 90 秒後開始消退。完成、Escape 或開信紙會退出，恢復原本的等信選擇；手上有瓶子時先讀完或放回。表情與沙痕不保存，信件與草稿照常保存。

信紙與信冊保留原有信件流程。短螢幕靠近前景時工具會縮小或移到側邊；設定減少動態時停止浪花往返與海鷗。畫質可在試玩工具調低。場景載入失敗或 WebGL context 中斷會顯示恢復提示。

場景素材原圖、提示、hash 與地圖資料見 [beach-v1](../assets/scenes/beach-v1/README.md)。新場景尚待使用者檢視美術與沉浸感，不代表已完成所有角色動畫。

```powershell
node --test prototype/model.test.cjs prototype/navigation.test.cjs prototype/environment.test.cjs prototype/interactions.test.cjs prototype/qa-support.test.cjs
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/paper_doll.py validate
python tools/paper_doll.py preview
node prototype/run-existing-checks.cjs
node prototype/check-living-beach.cjs
node prototype/run-http-checks.cjs
node prototype/record-preview.cjs
```

瀏覽器檢查依序執行，使用獨立 Chrome profile，拒絕連接已占用的測試 port，並核對自己啟動的 profile。新場景結果位於 [file 檢查](qa/living-beach/checks.json)與 [HTTP 檢查](qa/living-beach-http/checks.json)。手機檢查是桌面 Chrome 的 viewport／觸控模擬，尚非真機軟體鍵盤測試。

[動態錄影](qa/living-beach/playtest.webm)只包含 canvas 場景、表情與沙畫；DOM 信紙另見 [桌機信紙](qa/living-beach/paper-desktop.png)及 [手機信紙](qa/living-beach/paper-mobile.png)。錄影驗證資料在 recording.json；效能僅代表本次 headless 軟體 WebGL 環境，不能推估手機效能。

本輪最終結果：Node 24／24、Python 11／11、原有瀏覽器 31／31、file 與 HTTP 場景各 38／38；地圖結構 0 警告、兩處目標可達，獨立預覽 CDP 路線通過。Playwright 驗證因未安裝而略過，沒有將它當成通過。獨立審查的三項 Important 均已修正並補回歸驗證，沒有延後的 Minor。

本次錄影長約 27.4 秒、1280 × 800、VP9 WebM，回讀可解碼。headless 軟體 WebGL 平均 frame 間隔 163.2 ms，約 6.1 fps，最長 316.7 ms。這份錄影供確認互動與動態內容，實際 GPU／手機流暢度尚未驗證。
