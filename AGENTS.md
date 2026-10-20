# Vialogue 專案入口

- 產品現行規則：`VIALOGUE-CONCEPT.md`。
- 角色素材、圖層擴充與重建方式：先讀 `CHARACTER-ASSETS.md`。
- 角色圖層唯一設定入口：`assets/characters/traveler/catalog.json`。
- 組裝工具：`tools/paper_doll.py`；預覽：`assets/characters/traveler/preview.html`。
- 歷史試稿保留在 `design/characters/paper-doll-pilot/`，不要從最舊 combinations 或歷史 README 推斷現行版本。
- 後續待辦：`TODO.md`；表情 v4 暫用，其他表情修整已暫緩。

新增圖層、款式、z 順序或位移時，優先修改 catalog 與新增透明 PNG，保持組裝程式不寫死款式名稱。新增素材使用固定 128 × 160 畫布／腳底錨點 [64,148]，或明確設定裁小圖的 offset。原素材保留，採用新版本時更新來源紀錄。

目前 `head` 含髮型與部分臉、一般表情，`outfit` 含身體與完整穿搭。這是過渡粗分層，尚非純前後髮、五官、上衣褲鞋；不可把留空的可選圖層誤報為已完成美術，也不要把靜態組合驗證視為所有方向或動畫已完成。

修改後執行：

```powershell
python tools/paper_doll.py validate
python tools/paper_doll.py preview
python -m unittest discover -s tests -p test_paper_doll.py -v
```

若正式更新已採用的美術或設定，先核對來源，再更新對應驗證基準。瀏覽器擷取檔案在 `assets/characters/traveler/qa/ui-frames/`，變更後要重新擷取才能作為瀏覽器一致性測試基準。
