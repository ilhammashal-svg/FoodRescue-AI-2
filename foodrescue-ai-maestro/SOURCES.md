# مصادر الـ Skills والمقارنة

طريقة العمل: لكل دور قورنت ≥3 مرشحات من (أ) مكتبة Skills في حساب Claude الخاص بك (Plugin `smart-company-orchestra` v2.2.0 ونسخ `anthropic-skills:*`) و(ب) GitHub. اختير الأقوى أساسًا ودُمج فيه أقوى ما في الباقي، ثم ضُبط على مجال FoodRescue AI.

## المستودعات التي قُرئت فعليًا (استنساخ مباشر)
- `github.com/anthropics/skills` — قُرئت: skill-creator، internal-comms، brand-guidelines، theme-factory.
- `github.com/anthropics/knowledge-work-plugins` — قُرئت: sales/competitive-intelligence، operations/status-report، data/validate-data (+ فهرس كل SKILL.md).
- `github.com/github/awesome-copilot` — قُرئ: skills/meeting-minutes.
- مكتبة حسابك: قُرئت SKILL.md الـ14 لـ `smart-company-orchestra` وتعليمات مديرها.

## مصادر قُيّمت من صفحات الفهارس (لم تُستنسخ؛ أُخذت الفكرة من الوصف المنشور)
- `food-waste` — claudskills.com / skills-hub.ai (محاور تحليل الهدر والتبرع).
- `affaan-m/everything-claude-code › market-research` (إسناد المصادر والأدلة المعاكسة).
- `phuryn/pm-skills › competitor-analysis` (5 منافسين، تسعير، تمايز).
- `shubhamsaboo/awesome-llm-apps › meeting-notes` (ملخص تنفيذي مختصر).
- `ComposioHQ/awesome-claude-skills` و`travisvn/awesome-claude-skills` (فهارس للبحث).

## جدول الاختيار
| الوكيل | الأساس المختار | مدموج من |
|---|---|---|
| لوحة القيادة | smart-project-intake-dashboard | data:build-dashboard، frontend-design |
| حارس المدخلات | smart-dashboard-intake-sync | data:explore-data، xlsx |
| سكرتير الاجتماع | awesome-copilot/meeting-minutes | smart-meeting-secretary، awesome-llm-apps/meeting-notes |
| محلل البيانات | smart-sales-data-analyst | food-waste، data:validate-data، xlsx |
| راصد السوق | smart-market-intelligence-ps | everything-claude-code/market-research، knowledge-work/competitive-intelligence، pm-skills/competitor-analysis |
| مسؤول الولاء | smart-loyalty-officer | loyalty-officer، marketing:email-sequence |
| موزّع المهام | smart-monday-task-distributor | monday-task-distributor، productivity:task-management |
| مصمم البوستات | smart-social-post-designer | brand-guidelines، theme-factory، marketing:content-creation، marketing:brand-review |
| معدّ العرض | smart-deck-builder | operations:status-report، pptx، internal-comms |
| وكيل الفيديو | smart-heygen-video-producer | video-making، marketing:content-creation |
| مُجدول الاجتماعات | smart-calendar-invite-sender | mail-calendar-coordinator، legal:meeting-briefing |
| منسق البريد | smart-mail-calendar-coordinator | internal-comms، marketing:email-sequence |
| أمين الأرشيف | smart-file-archivist | file-archivist، google-workspace |
| واجهة المخرجات | smart-dashboard-output-publisher | data:build-dashboard، competitive-intelligence (روابط للتحقق) |
| مضيف الوكلاء | anthropics/skills skill-creator | cowork-plugin، data:data-context-extractor |

**ملاحظة صريحة**: مستودعات الطرف الثالث لم تُنسخ نصوصها؛ أُعيدت صياغة الأفكار فقط. ملفات docx/pdf/pptx/xlsx في anthropics/skills «source-available» وتُستدعى عبر Skills Claude المدمجة لا بنسخها.
