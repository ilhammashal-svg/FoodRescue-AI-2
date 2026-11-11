---
name: maestro-agent-host
description: FoodRescue AI orchestra agent 15 «مضيف الوكلاء» - when the user asks for a new agent (from the dashboard request box or in chat), receives the request, researches the best skill for that role, writes its SKILL.md with inputs, steps and done criteria, registers it in the FoodRescue AI Maestro plugin and the orchestra phases, and adds its phase, inputs, on/off switch and outputs section to the dashboard. Use when the user says وكيل جديد, أضف وكيلًا, new agent, add agent, or a request appears in the dashboard.
---

# مضيف الوكلاء (maestro-agent-host)

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| `anthropics/skills › skill-creator` — **المختار أساسًا** | بنية SKILL.md (frontmatter بوصف يحدد متى يُستخدم)، اختبار بأمثلة، تحسين الوصف |
| `cowork-plugin` (مكتبة Claude) | تسجيل الـ Skill داخل Plugin وإعادة تغليف `.plugin` |
| `data:data-context-extractor` (anthropics/knowledge-work-plugins) | وضعا Bootstrap/Iteration: إنشاء أو تعديل وكيل قائم دون كسره |

## المدخلات
- طلب من `config/agents.maestro-agent-host.inputs.new_agent_request` أو من المحادثة: الاسم، ماذا يفعل، الموصل (اختياري)، متى يعمل.
- `shared/agents.json`, `shared/data-contract.md`.

## الخطوات
1. حلّل الطلب بلا أسئلة: استنتج `id = maestro-<slug إنجليزي>`، `label` عربي، `phase` (بعد مَن يعتمد عليه)، `depends_on`, `connector`, `inputs` (2–5 حقول بقيم افتراضية), `output_kinds`. كل استنتاج → `config/assumptions`.
2. ابحث (WebSearch: `github claude skill <role>` + مكتبة Skills عبر `SearchSkills`/`ListSkills`) عن 3 مرشحين، قارنهم، اكتب `sources` بما أُخذ من كل واحد.
3. اكتب `spec.json` وشغّل: `python3 scripts/host_agent.py <plugin_root> spec.json` → ينشئ `skills/<id>/SKILL.md` من القالب ويضيفه إلى `shared/agents.json` ويطبع عمليات db.
4. أكمل SKILL.md بخطوات حقيقية ومعيار إنجاز قابل للفحص (قالب skill-creator).
5. نفّذ عمليات db (`agents_registry/<id>` و`config/agents` merge) → يظهر الوكيل تلقائيًا في الداشبورد: بطاقة بمدخلاته، مفتاح تشغيل، مرحلته، وقسم في «المخرجات».
6. أضف سطره إلى جدول الفريق في `MAESTRO.md` (المرحلة والاعتماد)، ارفع `version` في `plugin.json` (patch)، وأعد التغليف بـ `cowork-plugin` إلى `.plugin`.
7. اختبار: شغّل الوكيل الجديد في `/rehearsal` وحده على البيانات الوهمية؛ لا يجتاز → صحّح مرة.

## الحواجز
- لا يحذف أو يعدّل وكيلًا موجودًا (تعديل = طلب صريح؛ وحتى حينها نسخة احتياطية).
- قواعد `data-contract.md` §5 تُنسخ إلى كل وكيل جديد.

## معيار الإنجاز
- [ ] SKILL.md جديد بوصف + مدخلات + خطوات + معيار إنجاز + مصادر.
- [ ] مسجل في `shared/agents.json` و`MAESTRO.md` و`agents_registry`.
- [ ] يظهر في الداشبورد بمدخلاته ومفتاحه وقسم مخرجاته.
- [ ] `.plugin` أعيد تغليفه بإصدار أعلى.

## التسليم
اسم الوكيل، مرحلته، رابط الداشبورد، ملف `.plugin` المحدث.
