#!/usr/bin/env python3
"""maestro-scribe: validate the tasks.json the scribe wrote from the minutes.
Every task: id (FR-<date>-NN), title, owner_email in team/management list, due (YYYY-MM-DD >= meeting),
priority in {عاجلة,عالية,متوسطة,منخفضة}. Invalid owner/due -> flagged 'needs_owner'/'needs_due' (never dropped).
Also writes per-owner blocks.

usage: validate_tasks.py <tasks.json> <people.json> <meeting_date> <out_validated.json>
"""
import sys, json, re
from datetime import date

def main():
    tp, pp, md, out = sys.argv[1:5]
    T = json.load(open(tp)); P = json.load(open(pp))
    emails = {p["email"].lower(): p["name"] for p in P.get("team", []) + P.get("management", []) if p.get("email")}
    seen, res, blocks = set(), [], {}
    for i, t in enumerate(T.get("tasks", []), 1):
        t = dict(t); t.setdefault("id", f"FR-{md}-{i:02d}"); flags = []
        if not re.fullmatch(r"FR-\d{4}-\d{2}-\d{2}-\d{2}", t["id"]): flags.append("bad_id")
        if t["id"] in seen: flags.append("duplicate_id")
        seen.add(t["id"])
        oe = (t.get("owner_email") or "").lower()
        if oe not in emails: flags.append("needs_owner"); t["owner_email"] = ""
        else: t["owner_name"] = emails[oe]
        try:
            ok = date.fromisoformat(t.get("due", "")) >= date.fromisoformat(md)
        except Exception:
            ok = False
        if not ok: flags.append("needs_due")
        if t.get("priority") not in {"عاجلة", "عالية", "متوسطة", "منخفضة"}: t["priority"] = "متوسطة"; flags.append("priority_defaulted")
        t["flags"] = flags; res.append(t)
        if t["owner_email"]: blocks.setdefault(t["owner_email"], []).append(t["id"])
    out_d = {"meeting_date": md, "tasks": res, "per_owner": blocks,
             "valid": sum(1 for t in res if not {"needs_owner", "needs_due", "duplicate_id", "bad_id"} & set(t["flags"])),
             "flagged": [t["id"] for t in res if {"needs_owner", "needs_due"} & set(t["flags"])]}
    json.dump(out_d, open(out, "w"), ensure_ascii=False, indent=2)
    print(json.dumps({"tasks": len(res), "valid": out_d["valid"], "flagged": out_d["flagged"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
