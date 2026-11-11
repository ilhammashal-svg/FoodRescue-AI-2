---
name: maestro-showcase
description: FoodRescue AI orchestra agent 14 «واجهة المخرجات» - runs right after every other agent finishes and publishes that agent's outputs into the dashboard's «المخرجات» button, separated by agent name - video, posts, reports, Excel, deck, emails, meeting invite, tasks, market brief, minutes - by uploading viewable files (PDF, PNG, MP4, CSV, MD) to the dashboard file store and writing an outputs record with link and preview; also writes the week's KPI tiles. Applies the privacy filter. Use after every agent in a run, or the user mentions زر المخرجات, نشر المخرجات في الداشبورد, publish outputs.
---

# واجهة المخرجات (maestro-showcase)

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| `smart-dashboard-output-publisher` (مكتبة حسابك) — **المختار أساسًا** | النشر بعد كل وكيل فورًا، رفع الملفات القابلة للعرض، مربعات المؤشرات |
| `data:build-dashboard` (anthropics/knowledge-work-plugins) | بطاقات KPI بعلامة المصدر |
| `anthropics/knowledge-work-plugins › sales/competitive-intelligence` (قاعدة «روابط للتحقق») | كل مخرج يحمل رابطًا يمكن التحقق منه في مكانه |

## الخطوات (لكل وكيل منتهٍ بحالة ok/ok_with_warnings/skipped)
1. حوّل ما لا يُعرض: docx → PDF (`soffice --headless --convert-to pdf`)، xlsx → يبقى رابط Drive + CSV مختصر للمعاينة.
2. ارفع الملفات القابلة للعرض (PDF، PNG، MP4 ≤ 20MiB، CSV، MD) بـ `mcp__claude-artifacts__upload_asset` إلى الداشبورد؛ احفظ `asset_id`.
3. `python3 scripts/build_output_docs.py 13_run_log/<date>/run_manifest.json <agent> <date> 08_rules/people.json > ops.json` (يحجب الإيميلات والدفتر ونص الشكر الخاص وأسماء المؤسسات بلا موافقة).
4. `mcp__claude-artifacts__db_write` بالعمليات (مستند لكل مخرج: `outputs/<date>__<agent>__<n>`). وكيل متخطى → مستند واحد `status: skipped` بالسبب.
5. بعد المحلل: `kpis/<date>` = total_surplus_kg, human_kg, compost_kg, dispose_kg, meals_redirected, rescue_rate, surplus_rate, co2e_avoided_kg, wow, data_quality_score.
6. سطر في `log/<date>__<n>`: سطر الوكيل الواحد.

## الحواجز
- لا `ledger.csv`، لا `people.json`، لا بريد مؤسسة أو جهة، لا نص `private_email`.
- فشل النشر لا يوقف التشغيل (تحذير).
- ملف > 20MiB → رابط فقط.

## معيار الإنجاز
- [ ] لكل وكيل منتهٍ مستند واحد على الأقل في `outputs` باسمه.
- [ ] كل مستند يحوي `url` أو `asset_id`.
- [ ] فحص الخصوصية: لا نمط بريد إلكتروني في أي `preview` غير رسائل البريد المحجوبة.

## التسليم
عدد المستندات المكتوبة لكل وكيل.
