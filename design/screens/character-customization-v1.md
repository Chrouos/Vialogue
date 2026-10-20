# 紙娃娃設定畫面 v1

日期：2026-10-15。

[畫面](character-customization-v1.png)使用內建 ImageGen 產生。此為待使用者確認的靜態設計稿，非可操作介面或已拆分的角色素材。

沿用已選定的柔和像素海灘與乾淨介面。左側呈現同一位旅人的站立、坐姿與走路預覽；右側呈現性別、六種髮型、六種髮色、四種五官及六套穿搭，並提供隨機搭配與完成按鈕。

圖中男女選項是視覺提案，具體性別選項仍待確認。生成圖的髮型縮圖包含不同髮色，正式介面應依目前所選髮色統一顯示，讓髮型和髮色的控制保持分開。站坐走僅為姿勢示意，尚未驗證實際模組化素材或動畫。

## 完整提示詞

```text
Use case: ui-mockup. Generate ONE 16:9 landscape high fidelity visual design mockup for the Vialogue browser game's character customization screen. Reference image is the APPROVED visual art direction, not a target to preserve: warm soft pixel beach environment, original finely detailed nostalgic fantasy MMORPG sprite travelers, calm and intimate, minimal clean ivory UI. Make a NEW screen with a character customization overlay and precise readable Traditional Chinese type.

Layout: background the same kind of gentle peach late-afternoon pixel beach and sea, subdued behind a single large central rounded ivory panel taking about 78% of the canvas width and 78% height, generous spacing. Small Vialogue at top left outside the panel. Panel header exactly "我的旅人" and small close icon top right. Two clear columns within panel.
LEFT about 42%: large uncluttered preview of ONE original charming detailed 2D pixel traveler with chestnut brown medium hair, soft sage short cloak/scarf, cream linen shirt, brown trousers, small leather satchel, boots. Full body visible in standing three-quarter front pose, about 3.5 heads tall; warm fine pixel outlines, detailed hair and clothing clusters, original design, no weapons or battle armor, not realistic painted human or smooth vector. Show deliberate crisp pixel clusters. Character stands on a tiny quiet sandy patch and small shadow, no huge pedestal. Preview below has three small tabs "站立", "坐下", "走路", "站立" selected. Beneath tabs show TWO smaller alternate pose previews of this EXACT SAME character with same hair, face, colors, outfit and satchel: a readable seated three-quarter side pose and a readable mid-step walking pose. Small labels "坐姿預覽" and "走路預覽". Keep these alternates small and recognizably consistent; no separate costume concepts.
RIGHT about 58%: concise accessible customization controls with finely drawn miniature ORIGINAL pixel thumbnails, clean high resolution UI framing:
Row "性別" with simple segmented buttons "男", "女" as example visual options, gender does not lock hair or clothes.
Row "髮型" with exactly 6 square hairstyle thumbnail tiles in one row, one selected with muted teal outline. Include short, bob, long, curly, ponytail, swept styles, consistent face scale.
Row "髮色" with exactly 6 round swatches: brown, black, cream blond, copper, dusty rose, muted silver.
Row "臉" with exactly 4 face thumbnail tiles with subtly different friendly eyes and facial features, same sprite scale.
Row "衣服" with exactly 6 square outfit thumbnail tiles, full coordinated relaxed coastal traveler outfits, warm earthy muted colors, one selected. No weapon, stats, rarity or costs.
Bottom panel footer with a small dice icon and secondary button "隨機搭配", a small subdued line "之後隨時可以更換", and one restrained muted teal primary button "完成". Align footer and generous padding.
Clean simplified UI with calm visual hierarchy, no excessive dividers or dense decorations, restrained soft shadows. UI text and buttons crisp and legible, not forced into pixel font, artwork specifically finely detailed pixel sprites. This is an in-game screen, not website landing page, no marketing copy or device/browser frame. No names, usernames, game currency, experience, quests, combat stats, hats obscuring hairstyle, collage, multiple panels of different screens. Do not use the reference's existing beach travelers as new exact characters. Main purpose: evaluate character scale, paper doll choices, and whether SAME modular character works in sitting and standing poses.
```

