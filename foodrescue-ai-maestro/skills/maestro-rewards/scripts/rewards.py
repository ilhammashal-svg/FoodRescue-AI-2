#!/usr/bin/env python3
"""maestro-rewards: pick the week's best donor institution ("زبون الأسبوع" = most food rescued for
human use), skip suspicious ones automatically, award points once per run, write card brief.

usage: rewards.py <insights.json> <people.json> <ledger.csv> <outdir> <run_date>
Rules (overridable in people.json -> rewards_rules):
  points = 1 per kg human + 0.5 per kg compost (+20 bonus if dispose share < 10%)
  suspicious: dispose share > suspicious_dispose_share, or not in donors list, or type internal
"""
import sys, json, os, csv

def main():
    ins, ppl, ledger, out, run = sys.argv[1:6]
    I = json.load(open(ins)); P = json.load(open(ppl))
    R = {"per_kg_human": 1.0, "per_kg_compost": 0.5, "bonus_low_dispose": 20, "low_dispose_share": 0.1,
         "suspicious_dispose_share": I.get("config_used", {}).get("suspicious_dispose_share", 0.3), **P.get("rewards_rules", {})}
    donors = {d["id"]: d for d in P.get("donors", [])}
    os.makedirs(out, exist_ok=True)
    res = {"run": run, "status": "skipped", "skipped": [], "winner": None}
    if I.get("low_quality"):
        res["skipped"].append("جودة البيانات أقل من الحد — لا نقاط هذا الأسبوع")
        json.dump(res, open(os.path.join(out, "rewards.json"), "w"), ensure_ascii=False, indent=2); print(json.dumps(res, ensure_ascii=False)); return
    rows = []
    if os.path.exists(ledger):
        rows = list(csv.DictReader(open(ledger, encoding="utf-8")))
    if any(r["run"] == run for r in rows):
        res.update(status="ok", note="النقاط مُنحت سابقًا لهذا التشغيل — لا منح مزدوج")
        json.dump(res, open(os.path.join(out, "rewards.json"), "w"), ensure_ascii=False, indent=2); print(json.dumps(res, ensure_ascii=False)); return
    for c in sorted(I.get("by_institution", []), key=lambda x: (-x["human_kg"], -x["compost_kg"])):
        d = donors.get(c["institution_id"])
        share = c["dispose_kg"] / c["total_kg"] if c["total_kg"] else 1
        if not d:
            res["skipped"].append(f"{c['institution_id']}: غير مسجلة في الداشبورد"); continue
        if d.get("type") == "internal":
            res["skipped"].append(f"{c['institution_id']}: داخلية"); continue
        if share > R["suspicious_dispose_share"]:
            res["skipped"].append(f"{c['institution_id']}: نسبة إتلاف {share:.0%} مرتفعة — auto_hold"); continue
        if c["human_kg"] <= 0:
            continue
        pts = round(c["human_kg"] * R["per_kg_human"] + c["compost_kg"] * R["per_kg_compost"] + (R["bonus_low_dispose"] if share < R["low_dispose_share"] else 0))
        bal = sum(float(r["points"]) for r in rows if r["institution_id"] == d["id"]) + pts
        res.update(status="ok", winner={"institution_id": d["id"], "name": d["name"], "region": d.get("region"), "human_kg": c["human_kg"],
                                        "compost_kg": c["compost_kg"], "dispose_share": round(share, 3), "points": pts, "balance": bal,
                                        "consent_public": d.get("consent_public") == "yes", "email": d.get("email", "")})
        rows.append({"run": run, "institution_id": d["id"], "points": pts, "reason": f"{c['human_kg']} كغ للتوزيع + {c['compost_kg']} كغ سماد"})
        break
    if res["winner"]:
        with open(ledger, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["run", "institution_id", "points", "reason"]); w.writeheader(); w.writerows(rows)
        W = res["winner"]; public_name = W["name"] if W["consent_public"] else "شريك الأسبوع"
        meals = int(round(W["human_kg"] / I.get("config_used", {}).get("meal_kg", 0.4)))
        res["card_brief"] = {"title": "شكرًا لشريك الإنقاذ", "public_name": public_name,
                             "line": f"ساهم هذا الأسبوع بإنقاذ ≈{meals} وجبة ({W['human_kg']:.0f} كغ) وصلت لجهات موثوقة.",
                             "points_line": f"+{W['points']} نقطة إنقاذ — الرصيد {W['balance']:.0f}", "name_allowed": W["consent_public"]}
        res["private_email"] = {"to": W["email"], "subject": f"شكرًا لكم — {meals} وجبة أُنقذت هذا الأسبوع",
                                "body": f"فريق {W['name']} الكريم،\nبفضلكم وُجّه هذا الأسبوع {W['human_kg']:.0f} كغ من الطعام الصالح (≈{meals} وجبة) إلى جهات موثوقة، و{W['compost_kg']:.0f} كغ إلى السماد.\nأُضيفت {W['points']} نقطة إنقاذ إلى رصيدكم ليصبح {W['balance']:.0f}.\nمع التقدير، فريق FoodRescue AI"}
    json.dump(res, open(os.path.join(out, "rewards.json"), "w"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in ("status", "skipped")} | {"winner": (res["winner"] or {}).get("institution_id")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
