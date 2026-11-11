---
name: maestro-scheduler
description: FoodRescue AI orchestra agent 11 «مُجدول الاجتماعات» - creates the next weekly meeting chosen on the dashboard calendar as a real Google Calendar event with the team, management and extra invitees from the dashboard as attendees, so each receives an official calendar invitation (accept/decline), with an agenda built from open tasks and pending human approvals, a Google Meet link and links to the minutes, report, deck and video. Use whenever a run reaches scheduling, or the user mentions دعوة الاجتماع, الاجتماع القادم, Google Calendar, invite.
---

# مُجدول الاجتماعات (maestro-scheduler)

## المصادر المدمجة (قورنت 3)
| المصدر | ما أُخذ |
|---|---|
| `smart-calendar-invite-sender` (مكتبة حسابك) — **المختار أساسًا** | حدث حقيقي بمدعوين = دعوة رسمية، أقرب وقت فارغ عند التعارض، الزبائن لا يُدعون |
| `anthropics/skills › mail-calendar-coordinator` | فصل الدعوة عن رسائل البريد، روابط المخرجات داخل الوصف |
| `legal:meeting-briefing` (anthropics/knowledge-work-plugins) | جدول أعمال من البنود المفتوحة والقرارات المطلوبة |

## المدخلات
`runs/<date>.next_meeting` {date, time, duration_min (60), location, meet:true} من تقويم الداشبورد؛ `08_rules/people.json` (team + management + invitees)؛ `06_tasks/<date>/tasks_validated.json`؛ روابط المخرجات من `run_manifest.json`؛ `company.timezone` (Asia/Jerusalem).

## الخطوات
1. لا `next_meeting` → افتراض: نفس يوم الاجتماع الحالي + 7 أيام، 10:00، 60 دقيقة؛ سجّله في `config/assumptions`.
2. `mcp__Google_Calendar__list_events` على المدة: تعارض → `suggest_time` لأقرب وقت فارغ في نفس اليوم ثم اليوم التالي؛ سجّل التغيير.
3. ابحث `search_events` عن حدث سابق بنفس العنوان والتاريخ → حدّثه بدل التكرار.
4. `create_event`: العنوان «FoodRescue AI — الاجتماع الأسبوعي <date>»، المدعوون = بريد الفريق والإدارة والمدعوين **فقط**، Meet مفعّل (`add_meet`)، `sendUpdates: all` إن `calendar_mode = invite`، الوصف: جدول الأعمال (المهام المفتوحة، المتأخرة، عمليات بانتظار موافقة بشرية، قرارات السلامة) + روابط المحضر والتقرير والعرض والفيديو.
5. احفظ `12_calendar/<date>/invite.json` (event_id, html_link, meet_link, attendees_count).

## الحواجز
- المؤسسات المتبرعة والجهات المستقبلة **لا تُدعى**.
- أي بريد خارج الداشبورد يُحذف من المدعوين ويُسجل.
- فشل التقويم → إعادة مرة ثم `skipped`؛ البريد يكمل ويذكر ذلك.

## معيار الإنجاز
- [ ] حدث واحد (لا تكرار) بتاريخ ووقت صحيحين بتوقيت المنطقة.
- [ ] المدعوون ⊆ قائمة الداشبورد، وعددهم = الفريق + الإدارة + المدعوين الصالحين.
- [ ] رابط الحدث ورابط Meet محفوظان.

## التسليم
`outputs`: الدعوة (`invite`، url = html_link، preview = الموعد وجدول الأعمال).
