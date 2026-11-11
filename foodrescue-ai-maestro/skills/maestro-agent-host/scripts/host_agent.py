#!/usr/bin/env python3
"""maestro-agent-host: register a new agent in the plugin and produce the dashboard db ops.

usage: host_agent.py <plugin_root> <spec.json>
spec.json: {"id":"maestro-<slug>","label":"...","purpose":"...","phase":"3","depends_on":[...],
            "connector":"...","inputs":[{key,label,type,default}],"output_kinds":[...],
            "steps":["..."],"done_criteria":["..."],"sources":["..."]}
Writes skills/<id>/SKILL.md (if absent), appends to shared/agents.json, and prints db ops for
agents_registry/<id> and config/agents (merge). Never overwrites an existing skill.
"""
import sys, json, os, re
from datetime import date

def main():
    root, sp = sys.argv[1:3]
    S = json.load(open(sp))
    if not re.fullmatch(r"maestro-[a-z0-9-]{2,40}", S["id"]):
        sys.exit("id must look like maestro-<slug>")
    reg_p = os.path.join(root, "shared", "agents.json"); reg = json.load(open(reg_p))
    if any(a["id"] == S["id"] for a in reg["agents"]):
        sys.exit(f"{S['id']} already registered")
    d = os.path.join(root, "skills", S["id"]); os.makedirs(d, exist_ok=True)
    sk = os.path.join(d, "SKILL.md")
    if not os.path.exists(sk):
        steps = "\n".join(f"{i}. {s}" for i, s in enumerate(S.get("steps", []), 1)) or "1. (اكتب الخطوات)"
        done = "\n".join(f"- [ ] {c}" for c in S.get("done_criteria", [])) or "- [ ] المخرج موجود ومسجّل في run_manifest.json"
        ins = "\n".join(f"- `{i['key']}` — {i['label']} (افتراضي: {i.get('default','')})" for i in S.get("inputs", []))
        open(sk, "w", encoding="utf-8").write(f"""---
name: {S['id']}
description: FoodRescue AI orchestra agent «{S['label']}» - {S['purpose']} Connector: {S.get('connector','—')}. Use whenever the orchestra run reaches phase {S.get('phase','3')}, or the user mentions {S['label']}.
---

# {S['label']} ({S['id']})

## الغرض
{S['purpose']}

## المدخلات (من الداشبورد: `config/agents.{S['id']}.inputs`)
{ins or '- لا مدخلات خاصة'}
- يعتمد على: {', '.join(S.get('depends_on', [])) or '—'}
- عقد البيانات: `shared/data-contract.md`

## الخطوات
{steps}
- أضف كل مخرج إلى `run_manifest.json` بنوع من: {', '.join(S.get('output_kinds', ['data']))} ثم يستدعي المدير `maestro-showcase`.

## القواعد
قواعد `shared/data-contract.md` §5 كلها سارية. لا سؤال للمستخدم: كل افتراض يُكتب في `config/assumptions`.

## معيار الإنجاز
{done}

## المصادر
{chr(10).join('- ' + s for s in S.get('sources', [])) or '- مولّد بواسطة maestro-agent-host من القالب الموحد'}
""")
    order = max(a["order"] for a in reg["agents"]) + 1
    entry = {"id": S["id"], "label": S["label"], "phase": S.get("phase", "3"), "order": order, "depends_on": S.get("depends_on", []),
             "connector": S.get("connector", "—"), "output_kinds": S.get("output_kinds", ["data"]), "inputs": S.get("inputs", [])}
    reg["agents"].append(entry); json.dump(reg, open(reg_p, "w"), ensure_ascii=False, indent=2)
    defaults = {i["key"]: i.get("default", "") for i in S.get("inputs", [])}
    ops = [{"op": "set", "path": f"agents_registry/{S['id']}", "data": {**entry, "added_at": date.today().isoformat(), "custom": True}},
           {"op": "merge", "path": "config/agents", "data": {S["id"]: {"enabled": True, "inputs": defaults}}}]
    print(json.dumps({"skill": sk, "order": order, "db_ops": ops}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
