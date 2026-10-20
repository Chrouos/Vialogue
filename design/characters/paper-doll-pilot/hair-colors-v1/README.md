# 五種髮色初稿

2026-10-19 製作並經使用者確認採用五色色盤，玫瑰粉採調紅版本。

依使用者回饋，玫瑰粉已提高紅色、降低紫感；原版五張玫瑰粉頭部保留於 `rose-red-original/`，目前預覽與對照圖使用調紅版本。

- [五髮型 × 五色對照](hair-colors-review.png)
- [三套穿搭 × 五色對照](outfits-colors-review.png)
- [可操作預覽](../../../../assets/characters/traveler/preview.html)
- [色盤與明暗節點](palettes.json)

已核准頭部像素來自 `style-refinement-v1/heads`；內建 imagegen 只產生技術遮罩 `matte-source.png`，提示保存在 [matte-prompt.txt](matte-prompt.txt)。沒有重畫髮型或逐色生成新人物。128 × 160 遮罩保存在 `assets/characters/traveler/masks/hair`，色盤映射由 `tools/build_hair_colors.py` 重現。五種顏色保留髮束明暗，玫瑰粉偏紅、黑色保留冷灰高光。

輸出 25 款頭部，搭配三套衣服共 75 種靜態組合。原有 15 種咖啡色搭配逐像素相同；75 種瀏覽器畫布輸出均與 Python 組裝相同，髮型／髮色選項可分開切換。測試檢查透明度、遮罩外像素、眼睛與下半臉保護區。

仍是一般表情、單一方向靜態站姿。遮罩不等於完整前後髮、乾淨臉底或動態換裝；其他表情與動畫未在本輪套色。
