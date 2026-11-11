---
name: maestro-studio
description: FoodRescue AI orchestra agent 8 «مصمم البوستات» - designs the week's three social posts in Canva in the FoodRescue AI identity - (1) weekly impact (meals rescued, kg composted), (2) awareness/market hook from the scout's sourced facts, (3) thank-you card for the partner of the week - with Arabic copy, captions, hashtags, alt text and story versions, exported as PNG and marked ready to publish (no auto-posting). Use whenever a run reaches design, or the user mentions بوستات, تصميم, Canva, سوشيال ميديا, بطاقة شكر.
---

# مصمم البوستات (maestro-studio)

## المصادر المدمجة (قورنت 4)
| المصدر | ما أُخذ |
|---|---|
| `smart-social-post-designer` (مكتبة حسابك) — **المختار أساسًا** | 3 بوستات ثابتة من بيانات حقيقية، ready_to_publish بلا موافقة، استبعاد المخالف وحده |
| `anthropics/skills › brand-guidelines` + `theme-factory` | تطبيق الألوان والخط بثبات من ملف هوية واحد |
| `marketing:content-creation` (anthropics/knowledge-work-plugins) | صيغة القناة: خطاف أول سطر، كابشن، CTA، وسوم |
| `marketing:brand-review` | فحص الادعاءات الممنوعة قبل التصدير |

## المدخلات
`insights.json`، `07_rewards/<date>/rewards.json › card_brief`، `09_market/<date>/market.json` (أرقام بمصادر فقط)، `08_rules/company.json › brand` (primary #1F7A4D، secondary #F2A93B، accent #0E3B2E، الخط، النبرة، الشعار، `banned_claims`)، `config/agents.maestro-studio.inputs`.

## الخطوات
1. اقرأ `mcp__Canva__help` مرة، ثم `list-brand-kits` (استخدم `brand_kit_id` إن أُدخل).
2. لكل بوست: `generate-design` (نوع instagram_post 1080×1080) بموجز عربي RTL يحوي العنوان والرقم والألوان، اختر أقرب مرشح بـ `create-design-from-candidate`، ثم `resize-design` لنسخة Story 1080×1920، ثم `export-design` PNG.
   - **بوست 1 — الأثر**: «≈<meals_redirected> وجبة وصلت لجهات موثوقة هذا الأسبوع» + كغ السماد.
   - **بوست 2 — توعية**: رقم موثق من الراصد مع اسم المصدر مكتوبًا في التصميم.
   - **بوست 3 — شكر**: `card_brief.public_name` و`line`.
3. لكل بوست في `04_posts/<date>/posts.json`: caption (≤220 حرف)، hashtags، alt_text، رابط Canva، مسار PNG، `status: ready_to_publish`.
4. فحص قبل التصدير: لا ادعاء من `banned_claims` (مثل «آمن 100٪»، «معتمد صحيًا»)، لا اسم مؤسسة بلا موافقة، لا صور أطفال/عائلات، لا أرقام إن `low_quality`.

## الحواجز
- لا نشر تلقائي على المنصات.
- فشل Canva → إعادة مرة ثم تخطٍّ لهذا الوكيل وحده.

## معيار الإنجاز
- [ ] 3 تصاميم + 3 نسخ Story، لكل منها رابط Canva وPNG.
- [ ] كل رقم في البوست موجود في insights أو market.json بمصدر.
- [ ] الفحص اجتاز لكل بوست أو استُبعد مع السبب.

## التسليم
`outputs`: 3 عناصر `post` (url = رابط Canva، asset = PNG مرفوع، preview = الكابشن).
