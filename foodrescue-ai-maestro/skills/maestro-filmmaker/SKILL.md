---
name: maestro-filmmaker
description: FoodRescue AI orchestra agent 10 «وكيل الفيديو» - produces the week's short vertical promo video (30-45 s, 9:16, Arabic) for FoodRescue AI through the HyperFrames by HeyGen connector - script from the week's real impact numbers and the scout's sourced hook, brand colours, a call to action for institutions to register - composes and renders it and hands the project and MP4 links to the dashboard, invite and team email. Use whenever a run reaches video, or the user mentions فيديو, ريلز, HeyGen, HyperFrames, promo video.
---

# وكيل الفيديو (maestro-filmmaker)

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| `smart-heygen-video-producer` (مكتبة حسابك) — **المختار أساسًا** | 30–45 ث، 9:16، سكربت من insights، فشل = تخطٍّ دون إيقاف الدعوة والرسائل |
| `anthropics/skills › video-making` (مكتبة Claude) | هيكل الخطاف ← المشكلة ← الحل ← الدليل ← CTA، مشاهد قصيرة ≤ 6 ث |
| `marketing:content-creation` | CTA واحد واضح، نص على الشاشة ≤ 7 كلمات للمشهد |

## السكربت (5 مشاهد)
1. خطاف (0–5ث): رقم موثق من الراصد عن الهدر + المصدر على الشاشة.
2. المشكلة (5–12ث): فائض بلا سجل ولا مسار.
3. الحل (12–22ث): «سجّل ← صنّف ← وجّه»: توزيع / سماد / إتلاف آمن، «والقرار النهائي بشري».
4. الدليل (22–32ث): «هذا الأسبوع: ≈<meals> وجبة و<compost_kg> كغ سماد».
5. CTA (32–38ث): `cta` من مدخلات الوكيل + الشعار.

## الخطوات
1. `mcp__HyperFrames_by_HeyGen__get-send-to-hyperframes-guide` (مرة)، ثم `compose` بالسكربت، نسبة 9:16، لغة عربية، الألوان من الهوية، بلا وجوه أطفال أو عائلات، بلا أسماء مؤسسات.
2. `get_project_status` → `render_video` → `get_render_status` حتى الجاهزية. احفظ `project_url` و`mp4_url` في `10_video/<date>/video.json` مع السكربت.
3. نزّل MP4 إن أمكن وارفعه للداشبورد عبر الواجهة (≤ 20 MiB)، وإلا يُعرض الرابط.

## الحواجز
- `low_quality` → المشهد 4 بلا أرقام («كل وجبة تُنقذ تُحدث فرقًا»).
- لا ادعاء صحي («آمن 100٪») ولا وعد بتوصيل.
- فشل HeyGen → إعادة مرة ثم `skipped` مع السبب.

## معيار الإنجاز
- [ ] 30–45 ث، 9:16، عربي.
- [ ] كل رقم في الفيديو مصدره insights أو market.json.
- [ ] `project_url` و`mp4_url` (أو سبب التخطي).

## التسليم
`outputs`: الفيديو (`video`، url = mp4 أو المشروع، preview = السكربت).
