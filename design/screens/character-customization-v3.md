# 紙娃娃設定畫面 v3：臉部辨識度

日期：2026-10-15。

使用者反映 v2 表情太大眾、缺乏特色。以內建 ImageGen 編輯，保留介面與背景，調整四種臉的眉眼、嘴形與神情差異。

[畫面](character-customization-v3.png)為待確認的靜態試稿。四種提案為睏倦、倔強、好奇、調皮，尚未定為最終四種五官。正式素材仍需將基礎臉型與互動表情分開，並確保髮型與穿搭縮圖沿用所選臉；本圖縮圖尚未完全同步。

## 完整提示詞

```text
Edit this existing Vialogue character customization screenshot. Primary user feedback: faces are generic, nearly identical, lacking individual personality. Create a noticeable characterful FACE DESIGN pass, retaining clean nostalgic pixel sprites, NOT smooth anime portrait illustration.
STRICT INVARIANTS: keep beach background, warm palette, ivory UI layout, all Traditional Chinese text, controls, counts, hairstyle and clothing choices, standing/seated/walking composition. Only change facial designs and consistent corresponding previews; keep outfit/hair identity. Do not add panels or text.
The row labelled "臉" contains exactly FOUR face choices. All four have SAME brown hairstyle, same skin tone, same angle and crop, same scale so differences come from facial anatomy, eyebrows, eyes and mouth. Make four unmistakably different original pixel facial identities, readable at small sizes:
1 SELECTED "sleepy daydreamer": low half-lidded narrow eyes with flat heavy upper lids, slightly uneven soft brows, tiny straight off-center mouth, TWO or THREE little freckles across cheeks, calm wry slightly tired expression. Warm endearing and thoughtful, not sad or angry. Do NOT render large generic sparkling anime eyes. This is the selected face and must appear consistently on the large standing sprite, sitting and walking previews and outfit thumbnails.
2 "stubborn softie": thick short angular eyebrows, narrower upward-tilted eyes, small pursed pout mouth, a little cheek fullness. Looks quietly determined and a bit grumpy, still lovable; distinctly different eyebrow, eye shape and mouth from face 1.
3 "curious oddball": noticeably round smaller pupils in round open eyes, uneven raised eyebrows, tiny open o mouth, one small cheek beauty mark. Looks innocently surprised and absentminded. Keep eye highlights minimal, not glossy anime star eyes.
4 "mischievous friend": one eyebrow raised, asymmetrical squinting eyes with little upward outer corners, crooked one-sided closed-mouth grin, subtle single dimple. Cheerfully cheeky and eccentric, distinct from the others.
Differences should be large enough to recognize instantly without labels, avoiding four versions of same pleasant youthful anime face. Use expressive economical pixel clusters and clean eyebrows, face proportions and mouths. Do not rely just on eye color or accessories. No glasses or masks hiding features, no text descriptions or extra labels. Retain compact friendly original early-2000s MMORPG-like travelers, warm finely outlined pixel look and simple controlled shading. Important: the large standing sprite should visibly have half-lidded eyes and slight off-center wry mouth with freckles, with detail legible; all small previews of selected character should match to extent readable. No added high-frequency texture or shiny gradients. Keep interface typography sharp. One full screenshot only.
```

