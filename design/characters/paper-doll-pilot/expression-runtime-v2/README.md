# 傷心與超傷心：強化區別

- [傷心兩款前後對照](sadness-before-after.png)

- [八款小臉放大對照](faces-closeup.png)
- [遊戲原尺寸](native-size.png)
- [全身兩倍對照](full-body.png)

傷心改為睜眼低落、皺眉、閉嘴且不流淚；超傷心改為哭到閉眼、張嘴與藍白淚流，優先讓形狀有差別，允許誇張表現。其他六款沿用 v1 檔案，不重新生成。這輪小臉造型仍待使用者確認。

## 查閱參考

- [RO 官方情緒圖示指南](https://renewal.playragnarok.com/gameguide/howtoplay_interface02.aspx)：官方說明用情緒圖示表達，提供快捷鍵與指令。
- [MapleStory Worlds 官方表情文件](https://maplestoryworlds-creators.nexon.com/en/docs?postId=544)：角色表情可獨立切換。
- [楓之谷愛哭鬼臉型表情對照](https://forum.gamer.com.tw/Co.php?bsn=7650&sn=6451016)：玩家整理的模擬預覽，觀察閉眼、嘴形等大幅變化，不視為官方引擎細節說明。參考圖留在 references/maplestory-face-examples.png。
- [楓之谷臉部像素對照](https://www.inven.co.kr/board/maple/5974/1366496)：玩家整理的外觀參考。

外部素材只用作表情表現參考，未匯入為遊戲資產。原稿 source.png 由內建 ImageGen 修改 v1 原稿的兩款表情，提示詞存於 prompt.txt。build_review.py 僅合成眉眼嘴與臉頰範圍，延用原 30 色、兩個紅暈色，加入兩個淚水色，特別保留來源中的藍色覆蓋，避免眼淚量化成膚色。

輸出仍是 128 × 160、原頭身比例與透明輪廓，臉部特徵範圍外的像素保持一致；不改已認可人物檔案。qa.json 記錄另外六款檔案相同、八款不同、原輪廓與身體保留等檢查。僅試作短偏分與苔綠背心的靜態版本，未完成通用紙娃娃臉層或動畫。

原尺寸檢查：超傷心保留 27 個青藍淚色像素，並採閉眼與張嘴，可與無淚的傷心分開；另六款輸出檔案與 v1 完全相同。新版哭臉的誇張程度仍待使用者確認。
