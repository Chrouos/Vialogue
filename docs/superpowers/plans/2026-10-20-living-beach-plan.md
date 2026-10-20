# Living Beach Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking. 使用者已選擇 1：Native，由同一實作者執行，最後一次獨立審查。各項結果與取捨保留於 .superpowers/sdd/2026-10-20-living-beach-plan/progress.md。

**Goal:** 將現有本機漂流瓶試玩改成有自然動態、表情回應、短暫沙畫，以及信紙／信冊操作的像素海灘。

**Architecture:** 分層場景用 PixiJS 呈現，時間與輕互動由可測試的純 JavaScript 模型驅動，原有信件模型與儲存格式保留。原始地圖與 PNG 經工具打包為本地傳統 script，直接開檔時也不依賴網路或 fetch。先接回現有介面，再逐步替換互動與外觀。

**Tech Stack:** PixiJS 8.20.1 / WebGL、原生 JavaScript / DOM dialog、Node built-in test runner、Python / Pillow、內建 ImageGen、獨立 Chrome / CDP。

**Spec:** `docs/superpowers/specs/2026-10-20-living-beach-design.md`，使用者已核准；執行者同時閱讀規格與本計畫。

## Global Constraints

- 世界 1280 × 720，左上為原點；角色畫布 128 × 160，腳底錨點 `[64,148]`，nearest 取樣，禁止任意重縮頭身比例。
- 導航 `actorRadius:9`、`ySquash:0.5`，出生點 `[640,610]`；幾何與畫面共用資料，檢查完整路徑，不只檢查目的地。
- 美術來源：內建 ImageGen 補製，`art_source:host_image`；沿用圖標記 `existing`。保存原圖、提示與 SHA-256；不以程式繪製替代場景美術，不使用影片生成。
- 素材須有實際透明度，不得把棋盤格當透明背景。既有角色 catalog、來源與美術基準維持原樣。
- PixiJS 固定 8.20.1，下載瀏覽器版至本地並保存 MIT 授權與 hash；遊玩時不載 CDN，不要求玩家安裝或建置。
- 保留 `vialogue.local-playtest.v1`、Web Locks、信件／照片、草稿、收藏與 `readReturns`；場景預覽不可改動 `clockOffset` 或延長持瓶期限。
- 角色維持目前已接入的站姿與坐姿影格；不宣稱完成完整走路、各方向或全部 75 種造型的動態換裝。
- 本輪仍是本機示例，常駐小型「本機試玩・示例旅人」標記；無 Google、真實多人或公開沙畫同步。
- 聲音預設關閉；背景分頁不補播事件。減少動態模式取消浪花往返、海鷗飛行與彈跳，信件與互動仍可操作。
- DPR 上限 2；UI 命中區至少 44 CSS px；主要驗證桌面 1440 × 960、手機 390 × 844，並檢查 360 px 寬與短高度版面。
- 此目錄不是 Git repository。直接在目前工作區執行，不初始化 Git、不虛構 commit；每階段用測試結果與進度記錄作檢查點。

## Review Focus

1. 舊資料的位置落在新版岩石上：只重設角色位置，完整保留信件與草稿；Task 2 加重載測試。
2. 同一道浪連續多格覆蓋筆跡：同一波只減淡一次，第二道浪才清除；Task 4 加 cycle 去重與局部覆蓋測試。
3. 指標穿出沙地或收到 pointercancel：不跨越禁畫區接線，不留下仍在畫的狀態；Task 4 加分段與取消測試。
4. 寫信時收到瓶子或觸控工具列：不自動搶走信紙焦點，不讓按鈕穿透到人物移動；Task 5 加真實指標事件測試。
5. 多瓶返航、切背景、舊分頁與失去 WebGL context：通知逐一保留，資料寫入權不被搶走，恢復時不爆發補播；Task 2、5、6 分別加恢復、通知與保存測試。

## 檔案與共用介面

| 檔案 | 職責 |
|---|---|
| `assets/scenes/beach-v1/map-bundle.json` | 唯一導航與地圖物件資料，採 `generate2dmap.map_bundle.v2` |
| `assets/scenes/beach-v1/scene.json` | 圖層、圖源、顯示倍率、環境節奏、可畫區／濕沙帶及角色配置，參照 map bundle |
| `assets/scenes/beach-v1/provenance.json` | 原始來源、提示檔與 hash；原圖放 `sources/`，採用圖放 `layers/`、`effects/` |
| `tools/build_beach_scene.py` | 檢查資料與圖片，產生內嵌貼圖的 `prototype/scene-pack.js` 及導航 classic script |
| `prototype/vendor/pixi-8.20.1.min.js`、`pixi-LICENSE.txt` | 固定版本的本地 PixiJS |
| `prototype/vendor/map-runtime.mjs`、`map-runtime.js` | skill 既有導航 runtime 1.1.2 與產生的 UMD 版，保留來源與原有授權說明 |
| `prototype/navigation.js` | 地圖 runtime 的窄介面，修復舊位置、規劃路徑與逐段移動 |
| `prototype/environment.js` | 純日夜、浪線、雲與海鷗狀態 |
| `prototype/interactions.js` | 純表情、回應排程、畫畫模式與筆跡消退 |
| `prototype/scene.js` | Pixi 圖層、鏡頭、貼圖、命中測試與效果繪製 |
| `prototype/game-ui.js` | 角色旁選單、工具、信紙／信冊轉場、焦點與觸控介面 |
| `prototype/app.js` | 信件／保存與場景整合；不再自行逐格繪製整個世界 |
| `prototype/check-browser.cjs`、`check-living-beach.cjs` | 原有 31 項流程、新場景互動與故障流程 |
| `prototype/record-preview.cjs` | 以獨立 Chrome 錄製實際場景互動與擷取介面 |

純模型沿用 `model.js` 的 UMD 形式，同時支援 Node `require` 與瀏覽器傳統 script。不新增僅供測試呼叫的產品 API。

共用資料：`Point={x:number,y:number}`；`Actor={id,x,y,mode:'moving'|'sitting',head,outfit,phase}`；`Wave={id:string,cycle:number,points:Point[]}`；`ScenePack={version:1,world:{width:1280,height:720},map,config,textures}`。`textures` 以 ID 對應 `{src:dataURI,width,height,anchor,scale}`；世界與來源像素的換算只做一次。

## Task 1：可導航的分層素材與離線資源包

**Files:** Create `assets/scenes/beach-v1/{scene.json,map-bundle.json,provenance.json,README.md}`、`sources/`、`layers/`、`effects/`；Create `tools/build_beach_scene.py`、`tests/test_beach_scene.py`、`prototype/navigation.js`、`prototype/navigation.test.cjs`、上述 vendor 檔；Generate `prototype/scene-pack.js`、`prototype/vendor/map-runtime.js`。

**Interfaces:**

- `build_scene(scene_path:Path,out_path:Path)->dict`，輸出 script 設定 `globalThis.VialogueScenePack`，回傳 `{textures:int,bytes:int,sha256:str}`；缺檔、錯 anchor、來源 hash 不合、無效尺寸必須報錯。
- `createNavigation(bundle)->{isValid(point),segmentClear(a,b),findPath(a,b),restore(point)}`；`findPath` 回傳 `Point[]|null`，`restore` 有效時回原點，否則回 `[640,610]`。底層使用已驗證 runtime 的 `createMapRuntime`、`isValid`、`segmentClear`、`findPath`，不另造一套碰撞公式。
- ScenePack 與 navigation 是後續 Task 2、4 的輸入；scene.json 是環境與互動參數的唯一入口，不在程式重複寫死美術款式。

- [x] **1. 寫失敗測試。** `test_beach_scene.py` 用暫存的一像素 PNG 及最小 manifest 驗證實際打包、RGBA、來源 hash 與缺檔拒絕；`navigation.test.cjs` 用 200 × 120 的測試世界與 x=99、y=0、w=1、h=120 的直牆，斷言 `nav.isValid({x:50,y:60}) === true`、`nav.isValid({x:150,y:60}) === true`、`nav.segmentClear({x:50,y:60},{x:150,y:60}) === false`。實際海灘另驗證出生點與濕沙互動點有路徑。
- [x] **2. 驗證 RED。** Run `python -m unittest discover -s tests -p test_beach_scene.py -v`、`node --test prototype/navigation.test.cjs`；缺少打包與導航實作時必須失敗。測試 fixture 只用於資料契約，不當作遊戲美術。
- [x] **3. 補製素材與地圖。** 先讀 generate2dmap／generate2dsprite／imagegen 需要的指令，執行 `forge_doctor.py --host-tools image_gen --save assets/scenes/beach-v1/doctor.json`。用已確認海灘與人物作參考，以內建 ImageGen 生成中性的天空、遠景、海面、沙地、前景、雲、浪花、獨立日月與反光／燈光，以及海鷗展翅影格、四款表情和工具圖示。每張實測尺寸並設定等比 scale／offset；圖層對位與透明背景逐張檢視，禁止將帶夕陽的整圖當夜景底圖。保存原始輸出及提示，從採用圖描出沙地、濕沙與岩石幾何。
- [x] **4. 實作打包與導航。** 本地固定 PixiJS 8.20.1 並記錄來源、MIT 與 hash；從 skill 複製 map-runtime.mjs 1.1.2，產生語意相同的 UMD 版，保留原始檔作 Node 對照。資源包包含已採用角色圖與坐姿影格的資料 URI，不修改角色 PNG。內嵌 JSON 須正確逃逸，不 fetch 本地 JSON、不從 file URL 上傳 WebGL 貼圖。
- [x] **5. 驗證 GREEN 與地圖。** Run 上述兩套測試；`node --check prototype/scene-pack.js`。依序執行下列指令；檢視幾何疊圖與所有路線 `ok:true`。重跑使用新 vN 輸出，保留前次來源。

```powershell
python C:/Users/7157/.codex/skills/generate2dmap/scripts/map_bundle.py validate --bundle assets/scenes/beach-v1/map-bundle.json --report assets/scenes/beach-v1/qa/bundle.json
python C:/Users/7157/.codex/skills/generate2dmap/scripts/map_nav.py check --bundle assets/scenes/beach-v1/map-bundle.json --output-dir assets/scenes/beach-v1/qa/nav-v1
python C:/Users/7157/.codex/skills/generate2dmap/scripts/build_scene_preview.py --bundle assets/scenes/beach-v1/map-bundle.json --output-dir assets/scenes/beach-v1/qa/preview-v1 --verify --strict
```
- [x] **6. 記錄檢查點。** 將採用素材、來源、靜態預覽與 QA 結果寫入本階段 README；圖片結構正確不等於使用者已認可新的場景美術。

## Task 2：Pixi 動態場景、日夜與既有流程接回

**Files:** Create `prototype/environment.js`、`environment.test.cjs`、`scene.js`、`check-living-beach.cjs`；Modify `app.js`、`index.html`、`check-browser.cjs`。

**Interfaces:**

- `sampleDay(localMinute:number)->{skyTint,sunlight,moonlight,lights}`，以規格五個時段插值，分鐘值循環 1440。
- `createEnvironment(config,rng)->EnvironmentState`；`stepEnvironment(env,{dtMs,localMinute,visible,reducedMotion})->EnvironmentFrame`，frame 包含日夜值、`waves:Wave[]`、雲位置及海鷗影格／位置。visible=false 不排程新事件，恢復不補播。
- `createScene({canvas,pack,onIntent,reducedMotion,quality})->Promise<Scene>`；Scene 提供 `render(snapshot)`、`worldToScreen(point)`、`screenToWorld(point)`、`pause()`、`resume()`、`destroy()`。snapshot 為 `{player,actors,incoming,environment,emotes,strokes}`，後兩者先傳空陣列。
- `onIntent({type,point?,actorId?})` 的 type 為 `move`、`self-menu`、`open-bottle`、`draw-start`、`draw-move`、`draw-end`；app 處理信件命令，renderer 不保存信件。

- [x] **1. 寫失敗測試。** `environment.test.cjs` 斷言 sampleDay(0) 與 sampleDay(1440) 相同、05:00／07:00／16:30／18:30／20:00 前後連續、夜晚 sunlight=0；注入固定 rng 驗證首次鳥 12～25 秒及後續 35～90 秒、浪週期 7～12 秒、隱藏後不補播。瀏覽器測試加入缺 WebGL／貼圖損毀會顯示可重試訊息，舊位置落入岩石只重設位置。
- [x] **2. 驗證 RED。** Run `node --test prototype/environment.test.cjs`；獨立 Chrome 執行 `node prototype/check-living-beach.cjs`，新功能斷言失敗而不是無關語法錯誤。
- [x] **3. 實作場景與時間。** 載入本地 vendor、導航與 scene-pack，移除 app 的 `getContext('2d')`、舊 loop／整圖繪製與矩形移動限制，保留圖片處理所需的 loadImage。用導航路徑驅動原角色移動；分層容器與角色腳底 y 排序。水域效果裁切於海面，浪線同時供 renderer 與 Task 4 使用；雲／海鷗不驅動信件時鐘。夜間日照反光消失，燈光與月光另顯現。
- [x] **4. 接回原有畫面。** 先保留目前 DOM 信件介面，更新原測試的座標取得方式為 scene.worldToScreen；場景預覽使用獨立欄位，不能更動 state.clockOffset。明確處理畫面 resize、背景暫停、context lost／restored、載入失敗與重試；資料模型計時繼續按原規則運作。
- [x] **5. 驗證 GREEN。** Run `node --test prototype/model.test.cjs prototype/navigation.test.cjs prototype/environment.test.cjs`；獨立 Chrome 跑原 31 項與新場景檢查。舊資料重載後，信件數、草稿文字、收藏、sentAt、持瓶 deadline 不變。比對晨光／白天／日落／夜色，確認地面與人物沒有跟海面一起漂動。
- [x] **6. 記錄檢查點。** 本階段交付「動態海灘＋原有功能可玩」，更新 QA；此時 UI 外觀尚待 Task 5。

## Task 3：頭頂表情與示例旅人回應

**Files:** Create `prototype/interactions.js`、`interactions.test.cjs`、`game-ui.js`；Modify `scene.js`、`app.js`、`index.html`、`style.css`、`check-living-beach.cjs`。

**Interfaces:**

- `createInteractions(config,rng)->InteractionState`，包含 `mode:'explore'|'draw'`、emotes、pendingReplies、strokes、activeStrokeId、waitingBeforeDraw。
- `emitEmote(s,{actorId,kind,nowMs,source})->boolean`，kind=`wave|happy|surprise|company`，source=`player|sample|reply`；拒絕未知種類，source=reply 不再排程回應。
- `stepInteractions(s,{nowMs,environment,actors})->{emotes,strokes}`；Task 3 先處理表情，Task 4 擴充筆跡。
- `createGameUI({root,onCommand})->UI`，提供 `openEmotes({anchor,actorId})`、`closeEmotes()`、`render(status)`、`destroy()`；onCommand 的 `emote` 命令攜帶 kind，其他現有信件入口仍由 app 接手。

- [x] **1. 寫失敗測試。** `interactions.test.cjs` 驗證玩家 t=0 發出成功、2999ms 被拒、3000ms 成功；每位角色僅一張；3600ms 後退場；固定 rng 下回應延遲 1500～4000ms，reply 事件不接力，NPC 20000ms 內不能重發。瀏覽器驗證 E／方向鍵／Enter／Escape、自己的頭頂位置、手機邊緣選單與文字標籤。
- [x] **2. 驗證 RED。** Run `node --test prototype/interactions.test.cjs` 與新瀏覽器表情情境。
- [x] **3. 實作表情。** 貼圖 0.2 秒出現、3 秒停留、0.4 秒退場，跟隨人物；示例自主間隔 20～50 秒。附近以腳底距離 220 世界像素判定，玩家事件每次最多挑一個符合冷卻的 NPC，50% 機率回應；亂數可注入，沒有符合者就無回應。讓世界回饋自然，不以等待時長保證回應。
- [x] **4. 接入輸入與焦點。** 點自己和工具圖示開同一選單，選項至少 44px，輸入框內按 E 不開選單，選單點擊不穿透場景。常駐本機示例標記；表情事件不觸碰信件 lastActivity。
- [x] **5. 驗證 GREEN 並留截圖。** Run 模型全套與 `node prototype/check-living-beach.cjs`；包含 reduced-motion 下無彈跳但可發表情。保留人物、選單、表情與海灘同框畫面。

## Task 4：畫沙模式與浪花抹除

**Files:** Modify `interactions.js`、`interactions.test.cjs`、`scene.js`、`game-ui.js`、`app.js`、`index.html`、`style.css`、`check-living-beach.cjs`。

**Interfaces:**

- `beginDrawing(s,{player,incoming})->boolean`，持瓶時拒絕；成功儲存原 waiting。app 取消移動並坐下，將 player.waiting=false。
- `endDrawing(s)->{restoreWaiting:boolean}|null`；結束當前筆跡、退出 draw，重複呼叫無副作用。
- `beginStroke(s,{point,player,geometry,nowMs})->string|null`、`appendStroke(s,{point,player,geometry})`、`endStroke(s)`；geometry 使用 Task 1 的 drawRegions／wetRegions，越界時切開線段而不連接兩側。
- 筆跡 `{id,createdAt,segments:[{points:Point[],strength,waveHits:string[]}],forceFadeAt?}`；waveHits 記錄 `Wave.id+cycle`，區段可依覆蓋位置切分。`stepInteractions` 回傳可見線段與 alpha，renderer 不另計一套消退時間。

- [x] **1. 寫失敗測試。** 驗證 120px 範圍邊界、禁畫區穿越不接線、pointercancel 後 activeStrokeId=null、持瓶不可進入、退出恢復原 waiting=true／false。乾沙 t=90000ms 仍在、105000ms alpha=0.5、120000ms 消失。濕沙同一 id/cycle 更新十次只減淡一次，第二波清除覆蓋部分，未覆蓋區段仍在。
- [x] **2. 加上限測試並驗證 RED。** 新增第25筆時最舊完成筆跡於1000ms淡去，活躍筆不被清除；輸入超過256點經簡化仍保留首尾及禁畫區斷點。Run `node --test prototype/interactions.test.cjs`。
- [x] **3. 實作畫筆與沙痕。** 用世界座標與統一浪線，沙痕寬2世界像素、單色微凹紋理；只渲染玩家輸入的線，不以程式替代生成背景美術。最多24筆，採樣點依時間與距離簡化。濕沙每一波只記一次hit，保持部分線段被抹除的過程。
- [x] **4. 接入模式與取消。** pointer capture，up／cancel／visibilitychange 都結束當前筆；畫畫不移動、不拖鏡頭、不捲動頁面、不收新瓶。Escape／完成／開啟信紙均透過同一 endDrawing 恢復原等待選擇。沙痕與表情不寫入 localStorage、不延長持瓶期限。
- [x] **5. 驗證 GREEN。** Run 模型全套與真實 mouse／touch CDP 操作；用第一波只覆蓋一半的實例檢查像素與線段資料。重開後筆跡消失、信件／草稿不變。確認畫沙者可由出生點走到濕沙區。

## Task 5：信紙、信冊與遊戲工具整合

**Files:** Modify `game-ui.js`、`app.js`、`index.html`、`style.css`、`check-browser.cjs`、`check-living-beach.cjs`。

**Interfaces:**

- 擴充 UI：`openPaper(dialogId,trigger)`、`closePaper(dialogId)`、`openJournal(trigger)`、`render(status)`；保留現有 form／input ID，讓信件邏輯沿用。UI不直接修改信件，透過 onCommand 送 `write|wait|journal|draw|emote|sound|quality` 命令。
- Scene 增加 `animateBottle({kind:'depart',from:Point})`；app 先成功提交模型與 save，再觸發視覺，動畫失敗不撤銷寄信、不重送。
- status 為 `{waiting,incoming,cooldownMs,unreadReturnCount,drawing,soundOn,quality}`；信冊入口帶未讀標記，仍可直接開啟未讀返航瓶。

- [x] **1. 寫失敗行為測試。** 在 check-living-beach.cjs 以真實瀏覽器、DOM與鍵盤／指標事件斷言：信紙上按 E 不發表情、點工具不移動、點 Escape 保存但不放回持瓶、圖片關閉回原頁、畫畫開信紙必退出、手機送出鍵可捲動抵達。不新增假 DOM 或第三方 DOM 套件。
- [x] **2. 驗證 RED。** 獨立 Chrome 執行新增 UI 情境；讓不符合的舊彈窗／輸入狀態失敗。人類閱讀文案與樣式不寫 source-text 斷言。
- [x] **3. 重做外觀與轉場。** 小型物件工具替換大導覽，進場提示短暫出現後收起。信紙由下緣展開，保留海灘動態與可讀文字，移除全景模糊、厚圓角卡片與大型返航卡。信冊呈現漂流／返航／草稿，保留翻信、照片、續寫、取回與收藏；焦點與原生 dialog 語意可沿用。
- [x] **4. 整合通知與動畫。** 到信不打斷新信，頭旁瓶子有可操作對應 DOM 按鈕。返航逐一開啟後，仍有其他未讀就繼續提示；重開保持未讀／已讀。照片處理時禁止送出，單分頁保護與儲存空間不足提示維持。
- [x] **5. 驗證 GREEN。** 跑既有31項的全部行為與新 UI 情境，不能刪掉舊檢查來達成通過。日落／夜色桌機、390及360px手機、短高度與軟體鍵盤區域縮小各留圖；檢查44px命中、標籤、焦點、無橫向溢出。實際手機鍵盤無法驗證時明確標示，不能以視窗縮小宣稱真機已驗證。

## Task 6：整合驗證、動態展示與文件

**Files:** Create `prototype/record-preview.cjs`、`prototype/qa-support.cjs`；Modify `check-living-beach.cjs`、`prototype/README.md`、根 `README.md`、`VIALOGUE-CONCEPT.md`、`TODO.md`；Generate `prototype/qa/living-beach/` 檢查結果、日夜／互動截圖與 `playtest.webm`。

**Interfaces:** QA 腳本共用獨立 CDP 瀏覽器與實際 DOM／canvas，從命令列讀取 `--url` 及 `--qa-dir`；`check-living-beach.cjs --url <file-or-http> --qa-dir <new-dir>` 以 exit 0 和 `{passed:true,checks:[...]}` 回報，失敗 exit 1 且保存原因。QA helper 放 `prototype/qa-support.cjs`，不得增加產品專用測試後門。

- [x] **1. 補整合失敗測試。** 場景預覽時間變更後 sentAt、clockOffset、lastActivity 不變；背景恢復不補播鳥／表情；重新載入未讀返航和草稿保留；WebGL context lost／貼圖失敗有保存及恢復提示；離線與 file模式無外部請求。預覽倍率、波浪測試注入放在測試 harness 的真實模型呼叫，不隱藏在正式玩家入口。
- [x] **2. 完整執行。** Run `node --test prototype/model.test.cjs prototype/navigation.test.cjs prototype/environment.test.cjs prototype/interactions.test.cjs`、`python -m unittest discover -s tests -p 'test_*.py' -v`、`python tools/paper_doll.py validate`、`python tools/paper_doll.py preview`；逐一 `node --check` 所有新增／修改的產品與QA JS。地圖 validate／nav／preview 重跑至新的 QA vN，檢查所有 WARN／FAIL，逐項修正或明確列出。
- [x] **3. 跑兩種載入方式。** 開獨立 Chrome profile、port9347；本環境 headless 驗證曾需 `--no-sandbox --disable-gpu`，只用於隔離測試瀏覽器，不改玩家瀏覽器設定。先跑 file URL 原有31項與新場景流程；啟動僅綁127.0.0.1的4173本機HTTP，再以同一QA腳本跑HTTP、離線、reduced-motion及故障情境。結束只關自己建立的瀏覽器／伺服器，不碰使用者分頁。
- [x] **4. 錄製與人工檢視。** record-preview.cjs 驗證 MediaRecorder MIME 支援，使用場景 canvas.captureStream(30) 錄約18秒，含自然浪花、發表情與畫沙／消退；存為webm並回讀確認duration、非空影格與可解碼。DOM信紙／信冊另擷取畫面，清楚標註canvas錄影不包含DOM。若環境不支援錄影，只交付已驗證畫面與具體缺口，不捏造影片。檢視已知時點畫面、夜晚無夕陽殘影、浪只影響水域，以及主角／UI互不遮擋；記錄測試環境的幀時間，不宣稱未測裝置表現。
- [x] **5. 收尾。** 更新產品文件的本輪試作範圍、開啟方式、素材來源與限制，TODO僅勾選實際完成項目。安排一次獨立整體程式審查，修正重大問題後重跑受影響檢查；附上可玩入口、測試結果、錄影與仍未完成範圍供使用者評估沉浸感。沒有Git就不執行commit／branch流程。

## 執行檢查點與順序

依序執行 Task 1 → 2 → 3 → 4 → 5 → 6。Task 1、2 提供所有互動共用的世界、幾何、時間與事件邊界；後續互動需要同一組介面，適合由同一位實作者連續完成。每個階段先看測試失敗、完成最小實作、驗證成功，再記錄進度；遇到素材不合格或技術失敗先解決來源，不以降低驗收標準繼續。

計畫自查已對照規格的場景、美術、日夜、表情、沙畫、介面、資料相容、故障處理與QA範圍。使用者核准本文件並選定執行方式後，依對應執行技能開始實作。
