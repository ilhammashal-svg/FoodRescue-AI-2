---
name: maestro-control-panel
description: FoodRescue AI orchestra agent 1 «لوحة القيادة» - creates or reconnects the single-page Claude Artifact dashboard (with database and file storage) that holds every input of the orchestra - organisation and brand, emails of team, management, donor institutions and receiving partners (charities, orphanages, food banks, compost companies), current and previous week surplus files, meeting minutes, company files, next-meeting calendar, per-agent inputs and on/off switches - and the «المخرجات» view. Use when setting up the orchestra, or the user mentions لوحة القيادة, الداشبورد, dashboard, إدخال البيانات, setup.
---

# لوحة القيادة (maestro-control-panel)

## الغرض
مكان واحد لكل المدخلات والمخرجات. لا يسأل المستخدم شيئًا: يملأ القيم الافتراضية ويسجّل كل افتراض في `config/assumptions` حيث يراه في اللوحة.

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ | لماذا |
|---|---|---|
| `smart-project-intake-dashboard` (مكتبة Skills في حسابك، Station J) | فكرة لوحة Artifact واحدة بقاعدة بيانات + `runs/<date>` بحالة ready | الأقوى: مصمم للأوركسترا نفسها — **المختار أساسًا** |
| `data:build-dashboard` (anthropics/knowledge-work-plugins) | بطاقات KPI أعلى الصفحة، فلاتر، صفحة مستقلة | أفضل في عرض المؤشرات |
| `anthropics/skills › frontend-design` | اتجاه بصري واضح وتباين، لا قوالب عامة | جودة الواجهة |

## المدخلات
- ملف المشروع (docx) → يستخرج الاسم والمنتج والقطاعات والأهداف.
- `shared/agents.json` → قائمة الوكلاء ومدخلاتهم الافتراضية (تُقرأ ديناميكيًا؛ أي وكيل يضيفه «مضيف الوكلاء» يظهر تلقائيًا).
- `assets/dashboard.html` في الـ Plugin.

## الخطوات
1. إن وُجد `08_rules/dashboard.md` فيه `DASHBOARD_SLUG` → أعد الاتصال (db_get على `config/company`) وانتهِ.
2. انشر `assets/dashboard.html` كـ Artifact (publish_files، العنوان «FoodRescue AI — لوحة قيادة الأوركسترا»، أيقونة dashboard)، ثم `declare_capabilities` بـ `{db:{rules:[{path:"config",read:"view",write:"admin"},{path:"runs",read:"view",write:"admin"},{path:"outputs",read:"view",write:"admin"},{path:"kpis",read:"view",write:"admin"},{path:"log",read:"view",write:"admin"},{path:"agents_registry",read:"view",write:"admin"}]}, user:{}, assets:{}}`.
3. اكتب البذور بـ db_write (لا بذور داخل الصفحة): `config/company` من ملف المشروع، `config/people` بإيميل المالك في الإدارة فقط، `config/agents` (كل وكيل enabled + مدخلاته الافتراضية)، `agents_registry/*` من `shared/agents.json`، `config/assumptions` بالافتراضات.
4. احفظ `08_rules/dashboard.md`: `DASHBOARD_SLUG`, `DASHBOARD_URL`, تاريخ الإنشاء.
5. سجّل السطر: «أُنشئت لوحة القيادة: <الرابط>».

## الحواجز
- لا تكتب إيميلًا لم يُدخله المستخدم (إلا بريد المالك من سياق الجلسة كمدير افتراضي، ويُسجَّل افتراضًا).
- لا تحذف مستندًا في اللوحة أبدًا.

## معيار الإنجاز
- [ ] الصفحة منشورة وتعلن db+assets+user.
- [ ] `config/company`, `config/people`, `config/agents`, `config/assumptions` موجودة، و`agents_registry` = عدد الوكلاء في `shared/agents.json`.
- [ ] `08_rules/dashboard.md` محفوظ.
- [ ] قراءة اللوحة كـ view (`asLevel: view`) تنجح، والكتابة كـ view تُرفض.

## التسليم
`{agent, status, line, outputs:[{kind:"data", url:<dashboard>}]}`.
