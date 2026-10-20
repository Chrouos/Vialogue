# 海邊坐姿與待機試稿

2026-10-19 製作，待使用者檢視。短偏分、咖啡色、一般表情、米白 T-shirt＋牛仔褲＋白帆布鞋。

- [海灘動態預覽](preview.html)：可直接開啟，含放大人物、暫停與逐格查看。
- [放大 GIF](idle-preview.gif)
- [透明原尺寸 GIF](sitting-idle.gif)
- [坐姿放大圖](master-review.png)
- [影格對照](contact-sheet.png)
- [海灘靜態圖](beach-preview.png)

坐姿是一膝微抬、另一腿收起，一手放在膝上、一手撐地。新身體由內建 imagegen 參考已核准造型製作，實際原圖為 1254 × 1254；處理後換回核准短偏分頭部與一般表情，身體採同一份站姿色盤。原圖、提示、重建工具都保留於本資料夾。

動畫使用單一固定坐姿，3 個不同畫面依 5 段時間播放，總長 5.62 秒。上半身輕移一個像素模擬呼吸，閉眼區域取自原有影格；沒有逐幀重新生成紋理。腳底、下半身與撐地的手固定。這是微動試稿，未製作獨立風吹、完整胸腔動態或站立轉坐下的過程。

海灘由既有風格整合稿經內建 imagegen 移除人物與介面，作為比例預覽背景；尚非遊戲地圖或正式日夜系統。角色採固定 128 × 160 畫布與 [64,148] 地面錨點，沒有改動已確認的站姿素材與換裝 catalog，也未套用其他髮型、髮色、穿搭或表情。

## 重建與檢查

```powershell
python design/characters/paper-doll-pilot/sitting-idle-v1/build_pilot.py
python design/characters/paper-doll-pilot/sitting-idle-v1/verify_pilot.py
```

`animation.json` 記錄影格與時間；`qa.json` 記錄結構檢查。已核對透明度、固定接地區、呼吸位移、眨眼範圍、單一連通輪廓與 GIF 解碼像素。瀏覽器 5 個畫面與 PNG 相同，暫停、逐格查看及 390 px 手機寬度通過。這些檢查不代替使用者對姿勢和節奏的確認。
