---
name: maestro-rewards
description: FoodRescue AI orchestra agent 6 «مسؤول الولاء» - picks the week's best donor institution (the "customer" of FoodRescue - restaurant, canteen, hotel, university) by kilograms rescued for human distribution, automatically skips suspicious or unregistered ones, awards rescue points once per run in a ledger, and prepares the thank-you card brief (name only with public consent) and the private thank-you email. No connector. Use whenever a run reaches loyalty, or the user mentions أفضل زبون, أفضل مؤسسة متبرعة, نقاط, بطاقة شكر, loyalty.
---

# مسؤول الولاء (maestro-rewards)

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| `smart-loyalty-officer` (مكتبة حسابك) — **المختار أساسًا** | تعليق المشتبه `auto_hold` والانتقال للتالي، دفتر بلا منح مزدوج، موافقة النشر |
| `anthropics/skills › loyalty-officer` (نسخة المراجعة البشرية) | فصل بطاقة الشكر العامة عن الرسالة الخاصة |
| `marketing:email-sequence` (anthropics/knowledge-work-plugins) | رسالة شكر قصيرة بفائدة ملموسة وسطر واحد للخطوة التالية |

## تعريف «الزبون» في مشروعك
المؤسسة المتبرعة بالفائض (`config/people.donors`). الفائز = الأعلى `human_kg` هذا الأسبوع؛ التعادل → الأعلى سمادًا.

## الخطوات
1. `python3 scripts/rewards.py 13_run_log/<date>/insights.json 08_rules/people.json 07_rewards/ledger.csv 07_rewards/<date> <date>` (القواعد من `config/agents.maestro-rewards.inputs`).
2. القواعد: 1 نقطة/كغ للتوزيع + 0.5/كغ سماد + 20 مكافأة إن كانت نسبة الإتلاف < 10٪. يُتخطّى: غير المسجل، الداخلي، ونسبة إتلاف > `suspicious_dispose_share` (30٪) → `auto_hold`.
3. `rewards.json` يحوي `card_brief` (لمصمم البوستات) و`private_email` (لمنسق البريد فقط).

## الحواجز
- `low_quality` في insights → لا نقاط ولا بطاقة ولا رسالة.
- الاسم في البطاقة فقط إن `consent_public = yes`، وإلا «شريك الأسبوع».
- الدفتر والرسالة الخاصة وبريد المؤسسة **لا تُنشر في الداشبورد**.
- لا منح مرتين لنفس `run`.

## معيار الإنجاز
- [ ] فائز مؤهل أو سبب واضح لعدمه.
- [ ] سطر واحد جديد في الدفتر لهذا التشغيل (أو لا شيء إن وُجد سابقًا).
- [ ] `card_brief.name_allowed` يطابق الموافقة.

## التسليم
`outputs`: بطاقة الشكر (`card`، معاينة = النص العام فقط)؛ `rewards.json` داخلي.
