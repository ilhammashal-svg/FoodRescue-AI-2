# FoodRescue AI Maestro — أوركسترا منقذ فائض الطعام

16 وكيلًا (14 + مضيف الوكلاء + مصمم التطبيق المضاف) في Plugin واحد، يديرهم مايسترو، والداشبورد هو المدخل والمخرج الوحيد.

## التثبيت
1. ارفعي `foodrescue-ai-maestro.plugin` في Claude (الإعدادات ← Plugins / Customize ← رفع Plugin).
2. الصقي `MAESTRO.md` في تعليمات الـ Project «FoodRescue AI 2» (اختياري؛ الأوامر تقرؤه).
3. الداشبورد منشور مسبقًا: [private-link] — احفظي رابطه في `08_rules/dashboard.md` (موجود في القالب).

## الأوامر
- `/start-orchestra` إعداد/إعادة اتصال بالداشبورد.
- `/rehearsal` بروفة على بيانات وهمية بلا إرسال (55 فحصًا آليًا).
- `/perform` التشغيل الأسبوعي الحقيقي.
- `/add-agent <الوصف>` إضافة وكيل جديد عبر «مضيف الوكلاء».

## كل أسبوع
افتحي الداشبورد ← القسم 3: تاريخ الاجتماع + ملف الفائض الحالي والسابق + المحضر ← القسم 4: موعد الاجتماع القادم ← «جاهز للتشغيل». المهمة المجدولة تلتقطه وتنفذ `/perform`.

## الملفات
- `skills/maestro-*/SKILL.md` 16 وكيلًا + `scripts/` (Python قابل للاختبار)
- `shared/data-contract.md` عقد البيانات، `shared/agents.json` سجل الوكلاء
- `assets/dashboard.html` مصدر الداشبورد
- `ASSUMPTIONS.md` الافتراضات، `SOURCES.md` مقارنة المصادر
- `workspace-template/` مجلدات العمل + `examples/rehearsal/` (البيانات الوهمية وسكربتات البروفة)
