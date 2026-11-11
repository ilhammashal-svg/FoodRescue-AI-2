#!/usr/bin/env python3
"""maestro-app-designer: build the app's weekly data file (app_data.json) from the run's outputs.

usage: build_app_data.py <workspace> <date> <out_json> [agent_inputs.json]

Reads (all optional except insights): 13_run_log/<date>/insights.json, 13_run_log/<date>/run_manifest.json,
07_rewards/<date>/rewards.json, 06_tasks/<date>/tasks_validated.json, 08_rules/people.json, 08_rules/company.json.
Writes one JSON with two boards: team_board (team & manager) and customer_board (donors & partners).
The app's layout never changes week to week: only this file is swapped in.

Privacy filter (the app is public, no password):
- no e-mail address, no personal phone number anywhere (WhatsApp only from the organisation number input)
- donor names only with consent_public = yes; partners shown by type + region, name only with consent_public = yes
- no private thank-you e-mail text, no ledger, no children/family data
Exits with code 2 if the privacy check fails, so nothing unsafe is ever published.
"""
import sys, json, os, re
from datetime import datetime

ws, D, out = sys.argv[1:4]
agent_inputs = json.load(open(sys.argv[4])) if len(sys.argv) > 4 and os.path.exists(sys.argv[4]) else {}

def J(rel, default=None):
    p = os.path.join(ws, rel)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default

I = J(f"13_run_log/{D}/insights.json")
if not I:
    sys.exit("insights.json missing - analyst did not run; app data cannot be built")
M = J(f"13_run_log/{D}/run_manifest.json", {"agents": []})
R = J(f"07_rewards/{D}/rewards.json", {})
T = J(f"06_tasks/{D}/tasks_validated.json", {"tasks": []})
P = J("08_rules/people.json", {})
C = J("08_rules/company.json", {})

TYPE_AR = {"orphanage": "جمعية رعاية أيتام", "charity": "جمعية خيرية", "food_bank": "بنك طعام", "compost": "شركة سماد",
           "compost_company": "شركة سماد", "municipality": "بلدية", "collection_point": "نقطة جمع"}
LABEL = {"maestro-scribe": "سكرتير الاجتماع", "maestro-analyst": "محلل البيانات", "maestro-scout": "راصد السوق",
         "maestro-rewards": "مسؤول الولاء", "maestro-tasker": "موزّع المهام", "maestro-studio": "مصمم البوستات",
         "maestro-presenter": "معدّ العرض", "maestro-filmmaker": "وكيل الفيديو", "maestro-vault": "أمين الأرشيف",
         "maestro-scheduler": "مُجدول الاجتماعات", "maestro-courier": "منسق البريد"}
PUBLIC_KINDS = {"report", "excel", "deck", "video", "post", "card", "market", "minutes", "tasks", "invite"}

def yes(v):
    return v is True or str(v).strip().lower() in ("yes", "true", "1", "نعم")

# ---------- team & manager board ----------
kpi_keys = ["total_surplus_kg", "human_kg", "compost_kg", "dispose_kg", "meals_redirected",
            "rescue_rate", "surplus_rate", "co2e_avoided_kg", "operations", "institutions", "data_quality_score"]
kpis = {k: I.get(k) for k in kpi_keys}
tasks = [{"id": t.get("id"), "title": t.get("title"), "owner": t.get("owner_name") or "بلا مسؤول",
          "due": t.get("due") or "", "priority": t.get("priority") or "", "needs_fix": bool(t.get("flags"))}
         for t in T.get("tasks", [])]
outputs = []
for a in M.get("agents", []):
    for o in a.get("outputs", []):
        if o.get("private") or o.get("kind") not in PUBLIC_KINDS:
            continue
        outputs.append({"agent": a["agent"], "agent_label": LABEL.get(a["agent"], a["agent"]), "kind": o.get("kind"),
                        "title": o.get("title", ""), "url": o.get("url", ""), "preview": (o.get("preview") or "")[:300]})
team_board = {
    "kpis": kpis, "wow": I.get("wow", {}), "previous": I.get("previous", {}),
    "tracks": [{"key": "human", "label": "توزيع بشري", "kg": I.get("human_kg", 0)},
               {"key": "compost", "label": "سماد", "kg": I.get("compost_kg", 0)},
               {"key": "dispose", "label": "إتلاف آمن", "kg": I.get("dispose_kg", 0)}],
    "top_items": I.get("top_items", [])[:5], "top_waste_day": I.get("top_waste_day"), "top_reason": I.get("top_reason"),
    "reduction_plan": I.get("reduction_plan", []) if isinstance(I.get("reduction_plan"), list) else [],
    "tasks": tasks, "outputs": outputs,
    "pending_approval_note": "كل قرار توزيع/تحويل/إتلاف بانتظار موافقة بشرية (التصنيف توصية أولية تحتاج مراجعة بشرية).",
}

# ---------- customers board ----------
donors_ok = {d["id"]: d["name"] for d in P.get("donors", []) if yes(d.get("consent_public"))}
w = (R or {}).get("winner") or {}
card = (R or {}).get("card_brief") or {}
if w and w.get("institution_id") in donors_ok and card.get("name_allowed", True):
    pow_ = {"name": donors_ok[w["institution_id"]], "region": w.get("region", ""), "line": card.get("line", ""), "points_line": card.get("points_line", "")}
elif w:
    pow_ = {"name": "شريك الأسبوع", "region": w.get("region", ""), "line": card.get("line", ""), "points_line": ""}
else:
    pow_ = None
partners = []
for p in P.get("partners", []):
    partners.append({"label": (p["name"] if yes(p.get("consent_public")) else TYPE_AR.get(p.get("type"), "جهة شريكة")),
                     "type": TYPE_AR.get(p.get("type"), p.get("type", "")), "region": p.get("region", ""),
                     "verified": yes(p.get("verified"))})
regions = sorted({p["region"] for p in partners if p["region"]} | set(C.get("regions", [])))
media = [o for o in outputs if o["kind"] in ("post", "video", "card")]
wa = re.sub(r"\D", "", str(agent_inputs.get("whatsapp_number", "")))
customer_board = {
    "impact": {"meals_redirected": I.get("meals_redirected", 0),
               "rescued_kg": round((I.get("human_kg") or 0) + (I.get("compost_kg") or 0), 1),
               "co2e_avoided_kg": I.get("co2e_avoided_kg", 0),
               "co2e_note": "تقدير تقريبي بعامل قابل للتعديل"},
    "partner_of_week": pow_,
    "how_it_works": [{"step": 1, "title": "سجّل فائضك", "text": "المؤسسة تسجل الفائض ونوعه وكميته وظروف حفظه."},
                     {"step": 2, "title": "نطابقه مع شريك", "text": "نقترح المسار والجهة الأنسب حسب المنطقة والسعة، ويراجع إنسان القرار."},
                     {"step": 3, "title": "يُستلم ويُوزّع", "text": "تستلمه جمعية موثوقة أو يتحول إلى سماد."}],
    "ctas": {"register": "#register", "donate": "#donate", "whatsapp": (f"https://wa.me/{wa}" if wa else None)},
    "regions": regions, "partners": partners, "media": media,
}

data = {
    "meta": {"run": D, "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "test_mode": True,
             "test_banner": "نسخة تجريبية — البيانات المعروضة تجريبية",
             "title": agent_inputs.get("app_title") or C.get("name", "FoodRescue AI"),
             "tagline": C.get("tagline", ""), "brand": C.get("brand", {}),
             "banned_claims": (C.get("brand") or {}).get("banned_claims", [])},
    "team_board": team_board, "customer_board": customer_board,
}

# ---------- privacy gate ----------
txt = json.dumps(data, ensure_ascii=False)
txt_wo_wa = txt.replace(customer_board["ctas"]["whatsapp"] or "\x00", "")
problems = []
if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", txt):
    problems.append("email address")
if re.search(r"(?<![\w.:-])(?:\+|00)?\d{2,4}[\s-]?\d{3}[\s-]?\d{3,4}(?![\w.:-])", txt_wo_wa):
    problems.append("phone-like number")
for d in P.get("donors", []):
    if not yes(d.get("consent_public")) and d.get("name") and d["name"] in json.dumps(customer_board, ensure_ascii=False):
        problems.append(f"donor without consent: {d['id']}")
for c in data["meta"]["banned_claims"]:
    if c and c in json.dumps({k: v for k, v in data.items() if k != "meta"}, ensure_ascii=False):
        problems.append(f"banned claim: {c}")
if problems:
    print(json.dumps({"status": "blocked", "problems": problems}, ensure_ascii=False)); sys.exit(2)

os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"status": "ok", "out": out, "tasks": len(tasks), "outputs": len(outputs), "partners": len(partners),
                  "partner_of_week": bool(pow_), "whatsapp": bool(wa)}, ensure_ascii=False))
