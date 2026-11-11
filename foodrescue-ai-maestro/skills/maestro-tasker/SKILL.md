---
name: maestro-tasker
description: FoodRescue AI orchestra agent 7 «موزّع المهام» - writes the meeting's validated tasks, plus the analyst's urgent pickup and partner-verification actions, onto the monday.com board set in the dashboard (creating the board once if none), matches owners by team email, prevents duplicates by task ID, verifies what was written and reports overdue carry-over. Use whenever a run reaches task distribution, or the user mentions monday, مندي, لوحة المهام, توزيع المهام.
---

# موزّع المهام (maestro-tasker)

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| `smart-monday-task-distributor` (مكتبة حسابك) — **المختار أساسًا** | كتابة مباشرة بلا معاينة، إنشاء اللوحة مرة واحدة، منع التكرار بـ task ID |
| `anthropics/skills › monday-task-distributor` | تقرير الترحيل المتأخر والتحقق بعد الكتابة |
| `productivity:task-management` (anthropics/knowledge-work-plugins) | حالات بسيطة: مفتوح/قيد العمل/منجز، وتصنيف Waiting On |

## المدخلات
`06_tasks/<date>/tasks_validated.json`، `insights.json` (`urgent_human_ops`, `unmatched_ops`)، `08_rules/people.json`، `config/agents.maestro-tasker.inputs.board_id`.

## الخطوات
1. حمّل أدوات monday (`get_user_context`, `get_board_info`, `get_board_items_page`, `create_board`, `create_column`, `create_items`, `list_users_and_teams`).
2. لا `board_id` → `create_board` باسم «FoodRescue AI — مهام الأسبوع» بأعمدة: Task ID (text)، المسؤول (people)، الموعد (date)، الأولوية (status)، المصدر (text: اجتماع/فائض عاجل/تحقق جهة)، الحالة (status). سجّل المعرّف في `config/assumptions` وفي رسالة الإدارة.
3. اقرأ عناصر اللوحة؛ أي `Task ID` موجود → تحديث الحالة/الموعد فقط، لا عنصر جديد.
4. أضف المهام الصالحة. المسؤول: طابق البريد مع `list_users_and_teams`؛ غير موجود في monday → اكتب البريد في عمود نصي وتحذير.
5. أضف مهام تلقائية من المحلل: لكل عملية `urgent/high` للتوزيع «تأكيد فحص بشري + تنسيق استلام <op_id>» (للإدارة)، ولكل `unmatched` «إضافة/تحقق جهة مستقبلة».
6. تحقق: أعد قراءة اللوحة وطابق العدد.

## الحواجز
- مهام `needs_owner`/`needs_due` تُكتب في مجموعة «بحاجة لمسؤول» ولا تُسند لأحد.
- لا أسماء عائلات/أطفال في عناوين المهام.

## معيار الإنجاز
- [ ] عدد العناصر الجديدة + المحدثة = المهام الصالحة + التلقائية.
- [ ] لا Task ID مكرر على اللوحة.
- [ ] رابط اللوحة مسجل.

## التسليم
`outputs`: رابط اللوحة (`tasks`)، معاينة: عدد المضاف/المحدث/المتأخر.
