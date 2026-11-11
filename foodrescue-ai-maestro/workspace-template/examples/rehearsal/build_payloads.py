#!/usr/bin/env python3
"""Rehearsal: build the exact request payloads the connector agents would send (no external calls),
plus run_manifest.json for the run. usage: build_payloads.py <workspace> <date>"""
import sys, json, os
from datetime import date, timedelta

ws, D = sys.argv[1:3]
J = lambda p: json.load(open(os.path.join(ws, p)))
I = J(f"13_run_log/{D}/insights.json"); P = J("08_rules/people.json"); C = J("08_rules/company.json")
T = J(f"06_tasks/{D}/tasks_validated.json"); R = J(f"07_rewards/{D}/rewards.json"); M = J(f"09_market/{D}/market.json")
out = os.path.join(ws, "payloads"); os.makedirs(out, exist_ok=True)
allowed = {p["email"] for p in P["team"] + P["management"] + P.get("invitees", [])}
donor_partner = {d["email"] for d in P["donors"]} | {p["email"] for p in P["partners"]}
pct = lambda x: f"{x:.0%}" if x is not None else "—"

# tasker
items = [{"Task ID": t["id"], "name": t["title"], "owner": t.get("owner_email", ""), "due": t.get("due", ""), "priority": t["priority"],
          "source": "اجتماع", "group": "بحاجة لمسؤول" if {"needs_owner", "needs_due"} & set(t["flags"]) else "هذا الأسبوع"} for t in T["tasks"]]
items += [{"Task ID": f"FR-{D}-AUTO-{op}", "name": f"تأكيد فحص بشري + تنسيق استلام {op}", "owner": P["management"][0]["email"],
           "due": (date.fromisoformat(D) + timedelta(days=1)).isoformat(), "priority": "عالية", "source": "فائض عاجل", "group": "هذا الأسبوع"} for op in I["urgent_human_ops"]]
items += [{"Task ID": f"FR-{D}-AUTO-MATCH-{op}", "name": f"إضافة/تحقق جهة مستقبلة للعملية {op}", "owner": "", "due": "", "priority": "متوسطة",
           "source": "تحقق جهة", "group": "بحاجة لمسؤول"} for op in I["unmatched_ops"]]
json.dump({"tool": "monday.create_items", "board": "create:FoodRescue AI — مهام الأسبوع", "items": items}, open(f"{out}/maestro-tasker.json", "w"), ensure_ascii=False, indent=1)

# studio
card = R.get("card_brief", {})
low = I["low_quality"]
posts = [
 {"n": 1, "type": "impact", "headline": "كل وجبة لها طريق" , "number_line": None if low else f"≈{I['meals_redirected']} وجبة وصلت لجهات موثوقة + {I['compost_kg']:.0f} كغ للسماد هذا الأسبوع",
  "caption": f"هذا الأسبوع وجّهنا ≈{I['meals_redirected']} وجبة إلى جمعيات موثوقة، و{I['compost_kg']:.0f} كغ إلى السماد. سجّل مؤسستك وأنقذ فائضك.", "sources": ["insights.json"]},
 {"n": 2, "type": "awareness", "headline": "28٪ من هدر الطعام في العالم يأتي من خدمات الطعام", "number_line": "المصدر: UNEP Food Waste Index 2024",
  "caption": "المطاعم والمقاصف والفنادق مسؤولة عن 28٪ من الهدر العالمي (UNEP 2024). الخطوة الأولى: سجّل فائضك.", "sources": [M["numbers"][1]["url"]]},
 {"n": 3, "type": "thank_you", "headline": card.get("title", "شكرًا لشريك الإنقاذ"), "number_line": card.get("line"), "name": card.get("public_name"),
  "caption": f"شكرًا لـ{card.get('public_name','شريك الأسبوع')} — {card.get('line','')}", "sources": ["rewards.json"]}]
for p in posts:
    p.update(hashtags="#FoodRescueAI #لا_للهدر #إنقاذ_الطعام", alt_text=f"بطاقة بألوان FoodRescue الخضراء: {p['headline']}", sizes=["1080x1080", "1080x1920"],
             brand=C["brand"], status="ready_to_publish", canva_tool="generate-design → create-design-from-candidate → resize-design → export-design")
json.dump({"posts": posts}, open(f"{out}/maestro-studio.json", "w"), ensure_ascii=False, indent=1)

# presenter (8 slides)
k = I; w = I.get("wow", {})
slides = [
 f"# أُنقذ {k['human_kg']+k['compost_kg']:.0f} كغ من {k['total_surplus_kg']:.0f} كغ ({pct(k['rescue_rate'])})\n≈{k['meals_redirected']} وجبة · الحالة: {'🟢' if (k['rescue_rate'] or 0)>=0.7 else '🟡'}",
 f"# المسارات الثلاثة\nتوزيع {k['human_kg']} كغ · سماد {k['compost_kg']} كغ · إتلاف {k['dispose_kg']} كغ",
 "# الاتجاه\n" + ("، ".join(f"{a}: {b:+.0%}" for a, b in w.items() if not a.endswith('_pp')) or "لا مقارنة"),
 "# مصادر الهدر وخطة التقليل\n" + "\n".join("- " + x for x in I["reduction_plan"]),
 f"# الجهات والمطابقة\n{len(I['unmatched_ops'])} عملية بلا جهة · {len(I['urgent_human_ops'])} عاجلة/عالية",
 "# السوق\n" + "\n".join(f"- {n['value']} {n['unit']} — {n['claim']} ({n['source_name']})" for n in M["numbers"][:3]) + f"\n**الفرصة:** {M['opportunity']}",
 f"# قرارات بشرية مطلوبة\n{k['operations']} عملية بانتظار الموافقة · مهام بلا مسؤول: {', '.join(T['flagged']) or 'لا شيء'}",
 "# الخطوات القادمة\nProgress: التصنيف والمطابقة · Plans: مهام الأسبوع · Problems: شريك نقل بيت لحم · الاجتماع القادم 2026-11-16 10:00"]
json.dump({"tool": "Gamma.generate", "format": "presentation", "numCards": len(slides), "language": "ar", "textMode": "preserve",
           "inputText": "\n---\n".join(slides), "additionalInstructions": "RTL، ألوان #1F7A4D و#F2A93B، لا صور أشخاص"}, open(f"{out}/maestro-presenter.json", "w"), ensure_ascii=False, indent=1)

# filmmaker
scenes = [{"t": "0-5", "text": "28٪ من هدر الطعام من المطاعم والمقاصف", "source": "UNEP 2024"},
          {"t": "5-12", "text": "فائض بلا سجل… ولا مسار"},
          {"t": "12-22", "text": "سجّل ← صنّف ← وجّه: توزيع · سماد · إتلاف آمن — والقرار بشري"},
          {"t": "22-32", "text": "كل وجبة تُنقذ تُحدث فرقًا" if low else f"هذا الأسبوع: ≈{I['meals_redirected']} وجبة و{I['compost_kg']:.0f} كغ سماد"},
          {"t": "32-38", "text": "سجّل مؤسستك وأنقذ فائضك — FoodRescue AI"}]
json.dump({"tool": "HyperFrames.compose", "aspect": "9:16", "duration_s": 38, "language": "ar", "brand": C["brand"], "scenes": scenes,
           "rules": ["لا وجوه أطفال/عائلات", "لا أسماء مؤسسات"]}, open(f"{out}/maestro-filmmaker.json", "w"), ensure_ascii=False, indent=1)

# scheduler
att = [p["email"] for p in P["team"] + P["management"] + P.get("invitees", [])]
json.dump({"tool": "GoogleCalendar.create_event", "summary": "FoodRescue AI — الاجتماع الأسبوعي 2026-11-16", "start": "2026-11-16T10:00:00", "end": "2026-11-16T11:00:00",
           "timeZone": C["timezone"], "attendees": att, "conference": "meet", "sendUpdates": "all",
           "description": "جدول الأعمال:\n" + "\n".join(f"- {t['id']} {t['title']}" for t in T["tasks"]) + f"\n- {len(I['urgent_human_ops'])} عملية بانتظار موافقة بشرية\nالروابط: المحضر، التقرير، العرض، الفيديو"},
          open(f"{out}/maestro-scheduler.json", "w"), ensure_ascii=False, indent=1)

# courier
mode = C["automation"]["email_mode"]
msgs = []
for p in P["team"]:
    mine = [t for t in T["tasks"] if t.get("owner_email") == p["email"]]
    msgs.append({"to": [p["email"]], "kind": "team", "action": "create_draft" if mode == "drafts" else "send_message",
                 "subject": f"مهامك هذا الأسبوع ({len(mine)}) — FoodRescue AI {D}", "body": "\n".join(f"- {t['title']} — {t['due']}" for t in mine) + "\nروابط: الدعوة · البوستات · العرض · الفيديو"})
msgs.append({"to": [m["email"] for m in P["management"]], "kind": "management", "action": "create_draft" if mode == "drafts" else "send_message",
             "subject": f"FoodRescue AI {D}: أُنقذ {I['human_kg']+I['compost_kg']:.0f} كغ (≈{I['meals_redirected']} وجبة)",
             "body": f"العمليات بانتظار موافقتك: {I['operations']} (العاجلة: {', '.join(I['urgent_human_ops'][:8])}…)\nمهام بلا مسؤول: {', '.join(T['flagged'])}\nالتصنيف توصية لا شهادة صلاحية."})
if R.get("private_email"):
    msgs.append({"to": [R["private_email"]["to"]], "kind": "thank_you", "action": "create_draft" if mode == "drafts" else "send_message",
                 "subject": R["private_email"]["subject"], "body": R["private_email"]["body"], "private": True})
matches = {}
import csv
for r in csv.DictReader(open(os.path.join(ws, f"03_reports/{D}/FR_{D}_analyst_partner-matches.csv"), encoding="utf-8")):
    if r["suggested_partner"]: matches.setdefault(r["suggested_partner"], []).append(r)
pmail = {p["name"]: p["email"] for p in P["partners"]}
for name, rows in matches.items():
    msgs.append({"to": [pmail[name]], "kind": "partner_pickup", "action": "create_draft" if mode == "drafts" else "send_message",
                 "subject": f"طلب استلام فائض ({len(rows)} عملية) — FoodRescue AI", "body": "\n".join(f"- {r['food_item']} {r['qty_kg']} كغ ({r['classification_ar']})" for r in rows) + "\nالتصنيف توصية أولية؛ يُرجى الفحص عند الاستلام."})
json.dump({"mode": mode, "messages": msgs}, open(f"{out}/maestro-courier.json", "w"), ensure_ascii=False, indent=1)

# manifest
def o(path, kind, title, preview="", url="", private=False):
    return {"path": path, "kind": kind, "title": title, "preview": preview, "url": url, "private": private}
A = lambda a, st, line, outs: {"agent": a, "status": st, "line": line, "outputs": outs}
man = {"run": D, "mode": "rehearsal", "agents": [
 A("maestro-control-panel", "ok", "الداشبورد جاهز وتُقرأ منه المدخلات", []),
 A("maestro-gatekeeper", "ok", "طُوبق 20 عمودًا عربيًا وقُفل التشغيل", [o(f"13_run_log/{D}/mapping_current.json", "data", "مطابقة الأعمدة")]),
 A("maestro-scribe", "ok_with_warnings", f"محضر منسق و{len(T['tasks'])} مهام ({len(T['flagged'])} بلا مسؤول/موعد)", [o(f"06_tasks/{D}/tasks_validated.json", "tasks", "مهام الاجتماع", "؛ ".join(t['title'] for t in T['tasks'][:5]))]),
 A("maestro-analyst", "ok_with_warnings", f"صُنّفت {I['operations']} عملية: توزيع {I['human_kg']} · سماد {I['compost_kg']} · إتلاف {I['dispose_kg']} كغ", [
   o(f"03_reports/{D}/FR_{D}_analyst_surplus-log.xlsx", "excel", "سجل الفائض المنظف (Excel)"),
   o(f"03_reports/{D}/FR_{D}_analyst_surplus-report.docx", "report", "التقرير الأسبوعي", f"أُنقذ {I['human_kg']+I['compost_kg']:.0f} كغ؛ ≈{I['meals_redirected']} وجبة"),
   o(f"03_reports/{D}/FR_{D}_analyst_partner-matches.csv", "data", "مطابقة الجهات")]),
 A("maestro-scout", "ok_with_warnings", "6 منافسين و6 أرقام بمصادر (بحث الويب بديل Perplexity)", [o(f"09_market/{D}/FR_{D}_scout_market-brief.md", "market", "موجز السوق", " ".join(M["market_brief"]))]),
 A("maestro-rewards", "ok", f"شريك الأسبوع {R['winner']['institution_id'] if R.get('winner') else '—'}", [o(f"07_rewards/{D}/rewards.json", "card", "بطاقة الشكر", (card.get('public_name') or '') + " — " + (card.get('line') or ''), private=False)]),
 A("maestro-tasker", "ok", f"{len(items)} عنصرًا جاهزًا للوحة monday (بروفة)", [o("payloads/maestro-tasker.json", "tasks", "حمولة monday")]),
 A("maestro-studio", "ok", "3 بوستات + Stories جاهزة (بروفة)", [o("payloads/maestro-studio.json", "post", f"بوست {p['n']}", p["caption"]) for p in posts][:1] + [o("payloads/maestro-studio.json", "post", "بوستان 2 و3", posts[1]["caption"])]),
 A("maestro-presenter", "ok", f"عرض {len(slides)} شرائح (بروفة)", [o("payloads/maestro-presenter.json", "deck", "عرض الإدارة", slides[0])]),
 A("maestro-filmmaker", "ok", "سكربت فيديو 38 ث 9:16 (بروفة)", [o("payloads/maestro-filmmaker.json", "video", "سكربت الفيديو", " | ".join(s["text"] for s in scenes))]),
 A("maestro-scheduler", "ok", f"دعوة لـ {len(att)} مدعوين (بروفة)", [o("payloads/maestro-scheduler.json", "invite", "دعوة 2026-11-16 10:00", "الاثنين 2026-11-16 10:00–11:00 + Meet")]),
 A("maestro-courier", "ok", f"{len(msgs)} رسالة — الوضع: {mode}", [o("payloads/maestro-courier.json", "email", "رسائل الأسبوع", f"{len(msgs)} رسالة — الوضع: {mode}")]),
]}
json.dump(man, open(os.path.join(ws, f"13_run_log/{D}/run_manifest.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({"payloads": sorted(os.listdir(out)), "messages": len(msgs), "monday_items": len(items), "slides": len(slides)}, ensure_ascii=False))
