---
name: maestro-vault
description: FoodRescue AI orchestra agent 13 «أمين الأرشيف» - files every output of the run (inputs, cleaned surplus log, Excel, reports, minutes, tasks, market brief, posts, deck, video, emails log, invite, rules) into the standard folders and the Google Drive folder with the standard FR_date_agent_topic naming, never overwrites or deletes, resolves conflicts with _v2, and writes an archive index matching what the dashboard shows. Use at the end of every run, or the user mentions الأرشيف, ترتيب الملفات, التسمية, أين حُفظ.
---

# أمين الأرشيف (maestro-vault)

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| `smart-file-archivist` (مكتبة حسابك) — **المختار أساسًا** | التسمية بتاريخ الاجتماع، حماية الأصول، فهرس يطابق الداشبورد |
| `anthropics/skills › file-archivist` | حل تعارض الأسماء بلا كتابة فوق، فصل حسب النوع |
| `anthropics/skills › google-workspace` (مكتبة Claude) | الرفع إلى مجلد Drive فرعي بالتاريخ والاحتفاظ بالمعرّفات |

## الخطوات
1. `python3 scripts/archive.py <workspace> <date> 13_run_log/<date>/run_manifest.json` — ينسخ (لا ينقل) كل مخرج محلي إلى مجلده:
   `01_data/cleaned` (Excel/بيانات) · `02_minutes/final` · `03_reports` · `04_posts` · `05_decks` · `06_tasks` · `07_rewards` · `09_market` · `10_video` · `11_mail` · `12_calendar` · `13_run_log`.
2. Drive: في `drive_folder/<date>/` ارفع الملفات المؤرشفة (`create_file`)، عدا `07_rewards/ledger.csv` و`people.json` (تبقى محلية خاصة). سجّل `drive_id` و`url` لكل ملف في الفهرس.
3. المخرجات الخارجية (Canva، Gamma، monday، HeyGen، التقويم) تُفهرس بروابطها.
4. `13_run_log/<date>/archive_index.json` + نسخة MD قصيرة.

## الحواجز
- لا حذف ولا نقل ولا كتابة فوق؛ `01_data/original` و`00_inputs` للقراءة فقط.
- الملفات الخاصة (الدفتر، الإيميلات) لا تُرفع لمجلد مشترك.

## معيار الإنجاز
- [ ] كل `outputs` في المانيفست لها سطر في الفهرس (مؤرشف أو رابط خارجي).
- [ ] كل اسم يبدأ بـ `FR_<date>_`.
- [ ] عدد ملفات Drive = عدد المؤرشف القابل للمشاركة (أو تحذير).

## التسليم
`outputs`: الفهرس (`archive`، url = مجلد Drive).
