---
name: maestro-presenter
description: FoodRescue AI orchestra agent 9 «معدّ العرض» - builds the weekly management presentation in Gamma - exactly 8 Arabic RTL slides (headline impact, three-track split, trend vs last week, most-wasted items/days/reasons and reduction plan, partners and matching, market snapshot with sources, tasks and decisions needing human approval, next steps) in the brand colours, and exports PPTX and PDF. Use whenever a run reaches the presentation, or the user mentions عرض الإدارة, شرائح, Gamma, deck, presentation.
---

# معدّ العرض (maestro-presenter)

## المصادر المدمجة (قورنت 4)
| المصدر | ما أُخذ |
|---|---|
| `smart-deck-builder` (مكتبة حسابك) — **المختار أساسًا** | 8 شرائح ثابتة في Gamma، عربي RTL، تصدير pptx/pdf، فشل Gamma = blocked وحده |
| `operations:status-report` (anthropics/knowledge-work-plugins) | حالة 🟢/🟡/🔴، جدول هدف/فعلي/اتجاه، «قرارات مطلوبة» |
| `anthropics/skills › pptx` | عنوان = استنتاج، رقم واحد كبير لكل شريحة |
| `anthropics/skills › internal-comms (3P)` | Progress / Plans / Problems في شريحة الخطوات |

## المدخلات
`insights.json`، `06_tasks/<date>/tasks_validated.json`، `09_market/<date>/market.json`، `08_rules/company.json › brand`، `config/agents.maestro-presenter.inputs.theme`.

## الشرائح الثماني
1. **الأثر**: كغ منقذ + وجبات + حالة 🟢/🟡/🔴 (🟢 نسبة الإنقاذ ≥ 70٪).
2. **المسارات الثلاثة**: توزيع/سماد/إتلاف (كغ و٪).
3. **الاتجاه**: مقارنة بالأسبوع السابق أو «لا مقارنة».
4. **مصادر الهدر وخطة التقليل**: أعلى 3 أصناف + اليوم + السبب + `reduction_plan`.
5. **الجهات والمطابقة**: عدد العمليات المطابقة، غير المطابقة، الجهات غير الموثقة.
6. **السوق**: 3 أرقام بمصادرها + فرصة التمايز.
7. **المهام والقرارات البشرية المطلوبة**: عمليات بانتظار الموافقة، مهام بلا مسؤول.
8. **الخطوات القادمة** (Progress/Plans/Problems) + موعد الاجتماع القادم.

## الخطوات
1. `mcp__Gamma__get_themes` (طابق `theme` أو اختر أقرب ثيم أخضر).
2. `mcp__Gamma__generate` بـ `format: presentation`, `numCards: 8`, `language: ar`, `textMode: preserve`، ونص مقسّم بـ `---` لكل شريحة، والتعليمات: «RTL، الألوان #1F7A4D/#F2A93B، لا صور أشخاص».
3. `get_generation_status` حتى الاكتمال → `export_gamma` pptx ثم pdf → `05_decks/<date>/`.
4. تحقق بـ `read_gamma`: 8 بطاقات، كل رقم يطابق insights.

## الحواجز
- لا اسم مؤسسة بلا موافقة (الإدارة داخلية لكن العرض قد يُشارك).
- `low_quality` → شريحة 1 تحمل التحذير.
- شريحة بلا بيانات → «غير متاحة هذا الأسبوع» بدل الحذف.

## معيار الإنجاز
- [ ] 8 شرائح بالترتيب، عربية.
- [ ] رابط Gamma + pptx + pdf.
- [ ] كل رقم مطابق لـ insights/market.

## التسليم
`outputs`: العرض (`deck`، url = Gamma، asset = PDF).
