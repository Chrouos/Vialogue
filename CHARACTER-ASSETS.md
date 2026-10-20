# 角色素材與圖層入口

目前正式入口：

- [換裝預覽頁](assets/characters/traveler/preview.html)：直接開啟即可切換款式、下載透明 PNG，不需要啟動伺服器。
- [圖層與款式設定](assets/characters/traveler/catalog.json)：新增圖層、款式、圖片位置與前後順序都在這裡。
- [PNG 圖層](assets/characters/traveler/layers)：五款髮型各五色，共 25 款含臉頭部、三套完整穿搭。
- [通用組裝工具](tools/paper_doll.py)：依設定檔組裝，不寫死款式名稱。
- [素材來源紀錄](assets/characters/traveler/provenance.json)：保留來源與 SHA-256。

已接入最新確認的五款咖啡色髮型，以及 T-shirt＋牛仔褲、針織外套＋直筒褲、輕薄短外套＋短褲。用圖層重組的 15 種搭配與確認版本逐像素相同。

五色色盤已經使用者確認，玫瑰粉採調紅版本，可在預覽分開選髮型、髮色。75 種靜態搭配已完成組裝與瀏覽器比對，預設維持咖啡色。對照圖位於 [hair-colors-v1](design/characters/paper-doll-pilot/hair-colors-v1/README.md)。

## 現在做到哪裡

設定檔與組裝流程可以擴充。**現有美術尚未全部拆成細圖層**：

| 圖層 | 現有內容 | 還不能直接做的事 |
|---|---|---|
| `outfit` | 身體、手腳、上衣、褲子、鞋合在一起 | 任意交換上衣與褲子 |
| `head` | 髮型、部分臉部、一般表情合在一起；已匯出五色 | 任意換五官、前後髮；任意即時調色尚未接入 |
| `hair_back`、`face`、`hair_front`、`accessory`、`hat` | 已留空的可選圖層 | 需要先補對應透明 PNG |

換裝預覽現在只涵蓋 `stand-se` 靜態站姿與一般表情。原有八款表情與 GIF 仍保留在設計資料夾，未假裝已接入所有髮型和衣服。

新增獨立的[海邊坐姿／待機試稿](design/characters/paper-doll-pilot/sitting-idle-v1/README.md)：短偏分、咖啡色、T-shirt＋牛仔褲，含透明 GIF、影格與海灘預覽，待使用者檢視。此試稿尚未加入換裝 catalog；目前只有單一坐姿造型，不代表其他圖層已能跟著動作變形。

## 新增一個款式

把透明 PNG 放入相應資料夾，例如 `assets/characters/traveler/layers/hat/straw.png`，在 `hat` 的 `variants` 增加：

```json
{"id":"straw","label":"草帽","file":"layers/hat/straw.png"}
```

`file` 相對於設定檔；預設圖片左上角位於 `[0,0]`。以 128 × 160 同畫布作圖最方便，腳底錨點為 `[64,148]`，不在組裝時自動縮放人物。也支援裁小的 PNG 搭配 `"offset":[x,y]`，以及 `"opacity":0.8`。

新增後，執行下列兩個指令檢查並更新預覽：

```powershell
python tools/paper_doll.py validate
python tools/paper_doll.py preview
```

這只更新預覽，不重新生成既有圖像。預覽已嵌入圖片，可單獨開啟；修改設定或 PNG 後要重新執行 `preview` 才會更新。

## 新增整個圖層

在 `slots` 加一個項目，例如眼鏡：

```json
{
  "id":"glasses",
  "label":"眼鏡",
  "z":75,
  "required":false,
  "default":null,
  "variants":[
    {"id":"round","label":"圓框眼鏡","file":"layers/glasses/round.png"}
  ]
}
```

`z` 小的先畫、大的蓋在上面；同值依設定檔順序。`required:false` 可在預覽選「不使用」，`default:null` 表示預設關閉。圖層 ID 與款式 ID 使用小寫英文、數字、連字號或底線，且不能重複。新增此類圖層不需要修改組裝程式或預覽介面。

## 組裝並輸出

```powershell
python tools/paper_doll.py render --pick head=hc --pick outfit=jacket-shorts --out assets/characters/traveler/exports/character.png
```

有帽子素材後，可再加 `--pick hat=straw`，或用 `--pick hat=none` 關閉。錯字、缺檔、重複 ID 和停用必要圖層會報錯，不會悄悄忽略。其他角色或姿勢可使用自己的同格式設定檔：

```powershell
python tools/paper_doll.py --catalog path/to/catalog.json preview
```

## 後續拆細的方式

頭髮換色前先做純髮型遮罩，避免把咖啡色眼睛或膚色一起染掉。拆五官時先有乾淨的無五官臉底，不能把新眼睛直接蓋在舊眼睛上。拆上衣、褲子、鞋時，要先補完整身體與遮擋關係，再把 `outfit` 改成可選，增加 `body`、`pants`、`top`、`shoes` 等圖層。這些都可以延用同一個設定格式與組裝工具，但需要實際製作美術。

換姿勢與動畫需要該姿勢或動作的各圖層影格、共用錨點與遮擋順序。目前工具只處理靜態疊圖，沒有自動讓衣服跟著動作變形的功能。

已確認髮色五種：黑色、灰色、咖啡色、金黃色、偏紅玫瑰粉；詳見 [髮色規格](design/characters/paper-doll-pilot/planned-hair-colors.json)與 [TODO](TODO.md)。

## 已完成的髮色遮罩與選項入口

`masks/hair/{ha..he}.png` 是髮色遮罩，`tools/build_hair_colors.py` 只改遮罩內 RGB、保留透明度，咖啡色原圖不改。遮罩由內建 imagegen 產生，再做邊界保護與人工檢視；尚未拆成前後髮與乾淨臉底。前述「換色前先做遮罩」這一步已完成。

頭部 `selectors` 宣告髮型／髮色兩個選項軸，各 variant 的 `selection` 對應組合；預覽由資料建立分開的選單，組裝工具仍只讀 PNG ID。新增款式即使沒有 `selection`，仍可在「其他款式」選到。新髮型需另做遮罩與各色素材，工具不會自動辨識新圖頭髮。

本輪已用獨立 Chrome 驗證 75 種搭配逐像素相同、25 組獨立選項切換，以及 390 px 手機寬度。下面原有 15 種驗證紀錄對應咖啡色基準。

## 驗證與來源更新

```powershell
python -m unittest discover -s tests -p test_paper_doll.py -v
```

測試涵蓋任意新增圖層、前後順序、位移、關閉圖層、透明度、錯誤設定與既有 15 種圖像一致性。預覽 HTML 使用相同設定檔，不依賴外部圖片或網路。

已以獨立的無介面 Chrome 實測全部 15 種下拉選單組合，瀏覽器輸出與 Python 組裝逐像素相同，390 px 寬手機版無橫向溢出。桌面與手機擷取位於 `assets/characters/traveler/qa/`。有擷取檔時，測試也會檢查瀏覽器輸出；更新素材後需重新擷取，舊擷取不會自動代表新版。

`tools/export_paper_doll_sources.py` 是首次匯出已確認頭部、穿搭素材的工具，**平常新增款式不用執行它**。主動重跑時會更新八張既有基準 PNG，保留 catalog 與另加的款式；請勿把個人修改只存成同名基準圖後再重跑匯出。原始來源在 `design/characters/paper-doll-pilot/style-refinement-v1/`，之前確認的版本仍保留。
