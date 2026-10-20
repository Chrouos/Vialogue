# 五款神情：自然開朗

將刻意的 `^_^` 改為正常睜眼、放鬆眉毛與小幅張嘴笑的「開朗」。其他四款沿用 v2 的原始細節取樣，輸出與 v2 對應檔案逐一比對，保持相同。

- [五款放大](faces-closeup.png)
- [遊戲原尺寸](native-size.png)
- [完整人物](comparison.png)
- [全部髮型](all-hairstyles.png)

source.png 使用內建 ImageGen 針對原稿上排中間的人物修改；提示詞存於 prompt.txt。build_faces.py 只合成眉眼嘴區域，保留已認可的身體、髮型、比例與透明輪廓。五款造型仍待使用者確認，未套用動畫。50 張靜態提案為 5 髮型 × 5 神情 × 2 背心配色，並非兩套獨立服裝。
