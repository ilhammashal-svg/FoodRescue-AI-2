---
name: maestro-analyst
description: FoodRescue AI orchestra agent 4 «محلل البيانات» - cleans the weekly food-surplus log (the project's "sales" file), classifies every operation into the three tracks (human distribution / compost / safe disposal) with a written reason, priority and missing fields, matches each to the best receiving partner by region, capacity, accepted food, verification and transport, computes KPIs (kg rescued, meals redirected, compost kg, surplus rate, CO2e, week-over-week, most-wasted items, days and reasons), and exports a cleaned Excel workbook, a one-page Arabic report, a reduction plan and insights.json. Use whenever a run reaches analysis, or the user mentions سجل الفائض, تحليل الفائض, التصنيف, مؤشرات, تقرير أسبوعي, Excel.
---

# محلل البيانات (maestro-analyst)

## المصادر المدمجة (قورنت 4)
| المصدر | ما أُخذ |
|---|---|
| `smart-sales-data-analyst` (مكتبة حسابك) — **المختار أساسًا** | فحص قبل الحساب، درجة جودة، عزل الشاذ، insights.json للوكلاء، ورقة Config |
| `food-waste` (claudskills.com / skills-hub.ai) | محاور الهدر: أسباب مرمّزة، معدل التبرع والتحويل عن المكب، هرمية استرداد الغذاء |
| `data:validate-data` (anthropics/knowledge-work-plugins) | تحقق: المجاميع الفرعية = الإجمالي، مقارنة فترات متكافئة، لا متوسط متوسطات |
| `anthropics/skills › xlsx` | صيغ حية في Summary وعدم تعديل الأصل |

## المدخلات
`01_data/original/surplus_<date>.csv` (+ ملف الأسبوع السابق إن وُجد)، `08_rules/analysis_config.json` (العتبات + `partners` + `meal_kg` + `co2e_per_kg`).

## الخطوات
1. اقرأ Skill xlsx ثم شغّل:
   `python3 scripts/analyze_surplus.py 01_data/original/surplus_<date>.csv <prev.csv|-> 08_rules/analysis_config.json 03_reports/<date> <date>`
2. السكربت ينفّذ:
   - **الفحص**: تكرار رقم العملية، كمية صفرية/فارغة، وحدة مجهولة، `المنتج − المباع ≠ الفائض`، الحقول الحرجة الناقصة → درجة جودة 0–100 و`DataQualityLog`.
   - **التصنيف الثلاثي** (جدول خامسًا في ملف المشروع): إتلاف عند تلف/رائحة/تلوث كيميائي/لحوم وألبان تالفة/معلومات حرجة ناقصة؛ سماد للعضوي غير الصالح بشريًا وغير الملوث (أو المقدَّم للمستهلكين)؛ توزيع بشري لما هو محفوظ جيدًا وغير مقدَّم وضمن الفترة الآمنة ومغلف. لكل صف `classification_reason` مكتوب.
   - **الأولوية**: عاجلة (≤12 ساعة للصلاحية)، عالية (≤36)، متوسطة.
   - **المطابقة**: نقاط = المنطقة 40 + السعة 20 + التحقق 20 + النقل 10 + الحد الأدنى 10؛ جهة غير موثقة تُعلَّم «تحقّق قبل التواصل».
   - **المؤشرات**: إجمالي الفائض كغ، توزيع/سماد/إتلاف، الوجبات الموجهة، نسبة الإنقاذ، نسبة الفائض من الإنتاج، CO2e (عامل افتراضي معلن)، التغير الأسبوعي، أكثر الأصناف/الأيام/الأسباب هدرًا.
3. أجب عن `management_questions` في نهاية التقرير (سطران لكل سؤال أو «لا تكفي البيانات»).
4. المخرجات: `FR_<date>_analyst_surplus-log.xlsx` (Summary بصيغ حية، Cleaned، By_Track، By_Item، By_Day، By_Institution، By_Reason، Matches، Anomalies، DataQualityLog، Config)، `FR_<date>_analyst_surplus-report.docx` صفحة واحدة، `FR_<date>_analyst_partner-matches.csv`، `insights.json` (انسخه إلى `13_run_log/<date>/`). حوّل التقرير إلى PDF (`soffice --headless --convert-to pdf`) لعرضه في الداشبورد.

## الحواجز
- التصنيف **توصية أولية وليس شهادة صلاحية**؛ كل صف `manager_approval = pending`؛ الجملة التحذيرية في أسفل التقرير إلزامية.
- جودة < `min_quality_score` → تحذير بارز أول التقرير، `low_quality: true`: لا نقاط ولاء، لا أرقام في البوستات والفيديو.
- لا بيانات عائلات أو أطفال؛ المؤسسات بالرمز في insights.
- كل رقم في التقرير له خلية مصدر في Excel.

## معيار الإنجاز
- [ ] الملف الأصلي لم يتغير (hash قبل/بعد).
- [ ] مجموع `qty_kg` في Cleaned = `total_surplus_kg` = توزيع + سماد + إتلاف.
- [ ] كل صف له تصنيف وسبب وأولوية و`manager_approval=pending`.
- [ ] التقرير صفحة واحدة وفيه 3 استنتاجات (رقم + إجراء) وخطة تقليل.
- [ ] `insights.json` صالح.

## التسليم
`outputs`: Excel (`excel`)، التقرير docx+pdf (`report`)، المطابقات (`data`)؛ `metrics` = المؤشرات الرئيسية.
