---
name: maestro-app-designer
description: "FoodRescue AI orchestra agent 16 «مصمم التطبيق» - on the first run designs ONE FoodRescue AI web app in Claude Design that mirrors the dashboard and its «المخرجات» with two boards (team & manager board; customers board for donor institutions and receiving partners), publishes it automatically to Netlify and saves the link in the dashboard; on every later run only refreshes the data and outputs inside the same app and the same link - never a second site, never a redesign, never asks for approval. Connectors: Claude Design (Design artifact type) + Netlify. Use whenever a run reaches phase 4, or the user mentions مصمم التطبيق, تطبيق FoodRescue, رابط التطبيق, Netlify, Claude Design, لوحة الزبائن, لوحة الفريق."
---

# مصمم التطبيق (maestro-app-designer)

## الغرض
تطبيق ويب **واحد** لـ FoodRescue AI يُصمَّم مرة واحدة في Claude Design ويُنشر على Netlify تلقائيًا، ثم يتحدّث أسبوعيًا (بياناته ومخرجاته فقط) على **نفس الرابط**. يعمل تلقائيًا بالكامل بلا موافقة (قرار صاحبة المشروع 2026-11-09). التطبيق **تجريبي وبلا حماية**: كل ما فيه بيانات تجريبية ويمرّ بفلتر الخصوصية.

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| موصل **Netlify** الرسمي (`import-claude-design-from-url`) + نوع **Design** في Claude — **المختار أساسًا** | نشر تصميم Claude Design مباشرة؛ تمرير `claude_design_project_id` الثابت يحدّث نفس الموقع بدل إنشاء موقع جديد |
| `openai/skills › netlify-deploy` | تقرير النشر: رابط الموقع، حالة النشر، رابط السجلات؛ التحقق من الموقع الحي بعد النشر |
| `jezweb/claude-skills` (قائمة ملفات PWA) | جعل التطبيق قابلًا للتثبيت على الجوال: favicon، أيقونة 512، `site.webmanifest`، `theme-color` |

## المدخلات (من الداشبورد: `config/agents.maestro-app-designer.inputs`)
- `app_title` — اسم التطبيق (افتراضي: FoodRescue AI — منقذ فائض الطعام)
- `app_url` — رابط التطبيق؛ **يملؤه الوكيل** بعد أول نشر. فارغ = لم يُنشأ بعد.
- `design_project_id` — معرّف مشروع Claude Design؛ **يملؤه الوكيل**. هو مفتاح «نفس الموقع».
- `whatsapp_number` — رقم واتساب **المؤسسة** (لا رقم شخص). فارغ = زر واتساب يظهر «قريبًا».
- `redesign` — `true` = إعادة تصميم مرة واحدة في التشغيل القادم (على نفس الموقع ونفس الرابط)، ثم يعود `false`.
- يعتمد على: المحلل (insights)، الولاء (شريك الأسبوع)، المهام، البوستات، العرض، الفيديو — ويعمل في **المرحلة 4 بعد أمين الأرشيف**، فيصل رابطه إلى منسق البريد في المرحلة 5.
- يقرأ: `config/company`, `config/people`, `kpis/<run>`, `outputs/<run>__*`, `13_run_log/<run>/insights.json`, `run_manifest.json`, `07_rewards/<run>/rewards.json`, `06_tasks/<run>/tasks_validated.json`.

## محتوى التطبيق (ثابت التصميم، متغير البيانات)
تبويبان أعلى الصفحة، RTL، خط Tajawal، ألوان الهوية من `config/company.brand`، شريط علوي «نسخة تجريبية».

**أ) لوحة الفريق والمدير** (تحاكي الداشبورد وزر «المخرجات»):
مربعات المؤشرات (كغ منقذ، وجبات، كغ سماد، إتلاف، نسبة الإنقاذ، CO2e تقديري) مع سهم المقارنة بالأسبوع الماضي؛ توزيع المسارات الثلاثة؛ الأصناف الأكثر هدرًا وأكثر يوم وسبب؛ جدول المهام (المسؤول بالاسم فقط، الموعد، الأولوية، علامة «تحتاج استكمال»)؛ بطاقات المخرجات مجمعة باسم الوكيل (تقرير، Excel، عرض، فيديو، بوستات، محضر، دعوة) بروابطها؛ تنبيه «كل قرار بانتظار موافقة بشرية».

**ب) لوحة الزبائن** (المطاعم والفنادق والمؤسسات المتبرعة + الجمعيات وشركات السماد الشريكة):
عدّاد كبير للأثر (وجبات منقذة، كيلوغرامات، CO2e مع ملاحظة «تقدير»)؛ «شريك الأسبوع» مع بطاقة الشكر (الاسم فقط بموافقة)؛ «كيف تعمل الخدمة» في 3 خطوات؛ أزرار «سجّل مؤسستك» و«تبرّع بفائض الطعام» (نموذج بسيط داخل الصفحة يُعرض، بلا إرسال حقيقي في النسخة التجريبية) و«تواصل عبر واتساب»؛ المناطق والجهات الشريكة (بالنوع والمنطقة، الاسم فقط بموافقة)؛ آخر البوستات والفيديو التوعوي.

**قاعدة البيانات داخل التصميم**: كل الأرقام والنصوص المتغيرة تُقرأ من كتلة واحدة
`<script type="application/json" id="fr-data">…app_data.json…</script>`
فلا يتغير شيء في التخطيط عند التحديث الأسبوعي؛ تُستبدل هذه الكتلة فقط.

## الخطوات
1. **الحالة**: اقرأ `config/agents.maestro-app-designer`. `enabled:false` → `disabled`. حدّد الوضع:
   - `app_url` فارغ **و** `design_project_id` فارغ → **وضع الإنشاء (مرة واحدة)**.
   - غير ذلك → **وضع التحديث**. (`redesign:true` → إعادة التصميم داخل نفس `design_project_id`.)
   - احتياط ضد التكرار: قبل الإنشاء ابحث في Netlify (`netlify-project-services-reader › get-projects` باسم قريب من `app_title`)؛ إن وُجد موقع لهذا التطبيق → اعتمده واكتب افتراضًا، ولا تنشئ آخر.
2. **البيانات**: اكتب `08_rules/app_inputs.json` من مدخلات الوكيل، ثم
   `python3 -I scripts/build_app_data.py <workspace> <date> 14_app/<date>/app_data.json 08_rules/app_inputs.json`
   خروج بالرمز 2 (فشل الخصوصية) → لا نشر؛ `blocked` مع المشاكل المطبوعة. لا insights → `skipped` (لا تنشر أرقامًا قديمة).
3. **وضع الإنشاء — التصميم في Claude Design**:
   - `mcp__claude-artifacts__list_types` → نوع **Design**؛ `create_from_type` بعنوان `app_title`، واتبع تعليمات النوع العائدة حرفيًا.
   - صمّم صفحة واحدة بتبويبين (لوحة الفريق والمدير / لوحة الزبائن) كما في «محتوى التطبيق»، للجوال أولًا ثم الكمبيوتر، بالأرقام من `app_data.json` المضمّنة في كتلة `fr-data`، مع ملفات PWA (manifest، أيقونة، theme-color) والنص «نسخة تجريبية».
   - احفظ `design_project_id` = معرّف (slug) مشروع التصميم فورًا في `config/agents` (قبل النشر، كي لا يُعاد الإنشاء إن فشل النشر).
4. **وضع التحديث — البيانات فقط**: افتح نفس مشروع التصميم (`design_project_id`) واستبدل **كتلة `fr-data` فقط** بـ `app_data.json` الجديد. لا تغيّر التخطيط ولا الألوان ولا النصوص الثابتة (إلا مع `redesign:true`).
5. **النشر على Netlify (تلقائي)**: احصل على رابط الحزمة HTML المستقلة (صور وخطوط مضمّنة) من تصدير Claude Design («Send to Netlify»/التصدير وفق تعليمات النوع)، ثم
   `mcp__Netlify__import-claude-design-from-url` بـ `url`، `title = app_title`، و**دائمًا** `claude_design_project_id = design_project_id` (هذا ما يجعله يحدّث نفس الموقع). لا `password` (تطبيق تجريبي بلا حماية).
   تابع `mcp__Netlify__get-design-import-job-status` حتى `done` (أقصى 10 محاولات بفاصل). `failed` → إعادة مرة واحدة ثم `ok_with_warnings` (التطبيق السابق يبقى كما هو).
6. **حفظ الرابط**: وضع الإنشاء → `config/agents.maestro-app-designer.inputs.app_url` = الرابط العائد، و`redesign:false`. وضع التحديث → إن عاد رابط **مختلف** عن `app_url`: لا تغيّر `app_url` المحفوظ، اكتب تحذيرًا وافتراضًا في `config/assumptions` (يجب ألا يحدث مع نفس `claude_design_project_id`).
7. **التحقق من الموقع الحي**: `WebFetch(app_url)` وتأكد أن الصفحة تحوي عدد الوجبات لهذا الأسبوع وعبارة «نسخة تجريبية». لا يطابق → تحذير.
8. **التسليم**: أضف إلى `run_manifest.json` مخرجًا واحدًا `{"kind":"data","title":"🌐 تطبيق FoodRescue AI (لوحة الفريق + لوحة الزبائن)","url":app_url,"preview":"وضع: إنشاء|تحديث — وجبات N، كغ منقذ N، شريك الأسبوع …"}` ثم يستدعي المدير `maestro-showcase`. منسق البريد يضيف الرابط لرسالتي الفريق والإدارة.
9. **سطر واحد**: «أُنشئ التطبيق ونُشر: <الرابط>» أو «حُدّثت بيانات التطبيق على نفس الرابط: <الرابط>».

## القواعد
قواعد `shared/data-contract.md` §5 كلها سارية. لا سؤال للمستخدم: كل افتراض يُكتب في `config/assumptions`.
- **موقع واحد فقط إلى الأبد**: لا `import` بلا `claude_design_project_id`؛ لا حذف لأي موقع؛ لا موقع ثانٍ ولو فشل شيء.
- **نشر واحد لكل تشغيل** (كل نشر يستهلك رصيد Netlify المجاني ≈15). لا تغيير في البيانات منذ آخر نشر (نفس `run`) → لا نشر.
- **بلا حماية وبلا موافقة** (قرار صاحبة المشروع) → لذلك البيانات تجريبية فقط، وفلتر الخصوصية إلزامي: لا بريد إلكتروني، لا رقم هاتف لشخص، لا بيانات أطفال أو عائلات، لا نص الرسالة الخاصة ولا دفتر النقاط، لا اسم متبرع أو جهة بلا `consent_public = yes`.
- لا ادعاءات ممنوعة من `brand.banned_claims`؛ CO2e يُعرض دائمًا «تقديرًا».
- موصل Netlify أو نوع Design غير متاح → `skipped` مع اسم الموصل المطلوب (يظهر في رسالة الإدارة والداشبورد)، وباقي الأوركسترا يكمل.

## معيار الإنجاز
- [ ] `14_app/<date>/app_data.json` موجود واجتاز فلتر الخصوصية (خرج `status: ok`).
- [ ] فيه لوحتان: `team_board` (مؤشرات + مهام + مخرجات) و`customer_board` (أثر + 3 خطوات + أزرار + مناطق).
- [ ] `config/agents.maestro-app-designer.inputs.design_project_id` غير فارغ، و`app_url` غير فارغ بعد أول نشر ناجح.
- [ ] في وضع التحديث: الرابط بعد النشر = `app_url` المحفوظ (نفس الموقع).
- [ ] مخرج واحد بنوع `data` وعنوان «🌐 تطبيق FoodRescue AI» ورابط في `run_manifest.json`.
- [ ] نشر واحد على الأكثر في هذا التشغيل.

## التسليم
رابط التطبيق، الوضع (إنشاء/تحديث)، أهم 3 أرقام ظهرت فيه، وأي تحذير.
