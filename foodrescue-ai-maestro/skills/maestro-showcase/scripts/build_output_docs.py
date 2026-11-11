#!/usr/bin/env python3
"""maestro-showcase: turn one agent's manifest entry into db_write ops for the dashboard
(outputs/<run>__<agent>__<n>), applying the privacy filter (no ledger, no donor emails,
no private email bodies, no donor names without consent).

usage: build_output_docs.py <manifest.json> <agent> <run_date> <people.json> > ops.json
"""
import sys, json, re
from datetime import datetime, timezone

LABEL = {"maestro-app-designer": "مصمم التطبيق", "maestro-control-panel": "لوحة القيادة", "maestro-gatekeeper": "حارس المدخلات", "maestro-scribe": "سكرتير الاجتماع",
         "maestro-analyst": "محلل البيانات", "maestro-scout": "راصد السوق", "maestro-rewards": "مسؤول الولاء",
         "maestro-tasker": "موزّع المهام", "maestro-studio": "مصمم البوستات", "maestro-presenter": "معدّ العرض",
         "maestro-filmmaker": "وكيل الفيديو", "maestro-scheduler": "مُجدول الاجتماعات", "maestro-courier": "منسق البريد",
         "maestro-vault": "أمين الأرشيف", "maestro-showcase": "واجهة المخرجات", "maestro-agent-host": "مضيف الوكلاء"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
BLOCK_PATHS = ("ledger", "people.json", "donors", "private_email")

def main():
    mf, agent, run, pp = sys.argv[1:5]
    M = json.load(open(mf)); P = json.load(open(pp))
    hidden = [d["name"] for d in P.get("donors", []) if d.get("consent_public") != "yes"]
    a = next((x for x in M["agents"] if x["agent"] == agent), None)
    if not a: print("[]"); return
    ops, now = [], datetime.now(timezone.utc).isoformat()
    for n, o in enumerate(a.get("outputs", []), 1):
        if any(b in (o.get("path") or "") for b in BLOCK_PATHS) or o.get("private"):
            continue
        prev = EMAIL.sub("[بريد محجوب]", o.get("preview", ""))[:600]
        if o.get("kind") not in ("email",):  # management/team emails may name donors internally
            for h in hidden: prev = prev.replace(h, "شريك")
        ops.append({"op": "set", "path": f"outputs/{run}__{agent.replace('maestro-','')}__{n}",
                    "data": {"run": run, "agent": agent, "agent_label": LABEL.get(agent, agent), "kind": o.get("kind", "data"),
                             "title": o.get("title") or o.get("path", "").split("/")[-1], "url": o.get("url", ""),
                             "asset_id": o.get("asset_id", ""), "preview": prev, "status": a.get("status", "ok"), "created_at": now}})
    print(json.dumps(ops, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
