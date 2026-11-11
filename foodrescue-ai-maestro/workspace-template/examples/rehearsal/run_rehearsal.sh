#!/usr/bin/env bash
# FoodRescue AI Maestro — rehearsal on mock data. No external writes.
set -euo pipefail
PLUG="${1:?plugin root}"; WS="${2:?workspace}"; D="${3:-2026-11-09}"; EX="$PLUG/workspace-template/examples/rehearsal"
mkdir -p "$WS"; cp -rn "$PLUG/workspace-template/." "$WS/" 2>/dev/null || true
L="$WS/13_run_log/$D"; mkdir -p "$L" "$WS/03_reports/$D" "$WS/06_tasks/$D" "$WS/07_rewards/$D" "$WS/00_inputs/uploaded"
cp "$EX/surplus_current_week.csv" "$WS/00_inputs/uploaded/surplus_${D}_as_uploaded.csv"
cp "$EX/surplus_previous_week.csv" "$WS/00_inputs/uploaded/surplus_prev_as_uploaded.csv"
cp "$EX/minutes.md" "$WS/02_minutes/raw/minutes_$D.md"; cp "$EX/people.json" "$EX/company.json" "$WS/08_rules/"
sha_before=$(sha256sum "$WS/00_inputs/uploaded/surplus_${D}_as_uploaded.csv" | cut -d' ' -f1)
echo "▶ gatekeeper"
python3 -I "$PLUG/skills/maestro-gatekeeper/scripts/map_columns.py" "$WS/00_inputs/uploaded/surplus_${D}_as_uploaded.csv" "$WS/01_data/original/surplus_$D.csv" "$L/mapping_current.json"
python3 -I "$PLUG/skills/maestro-gatekeeper/scripts/map_columns.py" "$WS/00_inputs/uploaded/surplus_prev_as_uploaded.csv" "$WS/01_data/original/surplus_prev.csv" "$L/mapping_prev.json"
python3 -I - "$PLUG" "$WS" <<'P'
import json,sys; plug,ws=sys.argv[1:3]
reg=json.load(open(f"{plug}/shared/agents.json")); c=json.load(open(f"{ws}/08_rules/company.json")); p=json.load(open(f"{ws}/08_rules/people.json"))
agents={a["id"]:{"enabled":True,"inputs":{i["key"]:i.get("default") for i in a["inputs"]}} for a in reg["agents"]}
json.dump(agents,open(f"{ws}/08_rules/agents.json","w"),ensure_ascii=False,indent=1)
an=agents["maestro-analyst"]["inputs"]
json.dump({"thresholds":{k:an[k] for k in ("room_temp_max_h","cooked_chilled_max_h","min_quality_score")},"meal_kg":an["meal_kg"],"co2e_per_kg":an["co2e_per_kg"],"partners":p["partners"]},open(f"{ws}/08_rules/analysis_config.json","w"),ensure_ascii=False,indent=1)
P
echo "▶ analyst"
python3 -I "$PLUG/skills/maestro-analyst/scripts/analyze_surplus.py" "$WS/01_data/original/surplus_$D.csv" "$WS/01_data/original/surplus_prev.csv" "$WS/08_rules/analysis_config.json" "$WS/03_reports/$D" "$D"
cp "$WS/03_reports/$D/insights.json" "$L/insights.json"
echo "▶ rewards"
python3 -I "$PLUG/skills/maestro-rewards/scripts/rewards.py" "$L/insights.json" "$WS/08_rules/people.json" "$WS/07_rewards/ledger.csv" "$WS/07_rewards/$D" "$D"
echo "▶ rewards (re-run: must not double award)"
python3 -I "$PLUG/skills/maestro-rewards/scripts/rewards.py" "$L/insights.json" "$WS/08_rules/people.json" "$WS/07_rewards/ledger.csv" "$WS/07_rewards/${D}_rerun" "$D"
mkdir -p "$WS/09_market/$D"; cp -n "$EX/market_fixture/"* "$WS/09_market/$D/" 2>/dev/null || true
echo "▶ scribe"
cp "$EX/scribe_tasks_fixture.json" "$WS/06_tasks/$D/tasks.json"
python3 -I "$PLUG/skills/maestro-scribe/scripts/validate_tasks.py" "$WS/06_tasks/$D/tasks.json" "$WS/08_rules/people.json" "$D" "$WS/06_tasks/$D/tasks_validated.json"
sha_after=$(sha256sum "$WS/00_inputs/uploaded/surplus_${D}_as_uploaded.csv" | cut -d' ' -f1)
[ "$sha_before" = "$sha_after" ] && echo "original untouched: yes" > "$L/original_check.txt" || echo "original untouched: NO" > "$L/original_check.txt"

echo "▶ connector payloads (dry-run), vault, QA"
python3 -I "$EX/build_payloads.py" "$WS" "$D"
python3 -I "$PLUG/skills/maestro-vault/scripts/archive.py" "$WS" "$D" "$L/run_manifest.json"
echo "▶ app-designer (data only, no Claude Design / Netlify call)"
mkdir -p "$WS/14_app/$D"; echo '{"app_title":"FoodRescue AI — منقذ فائض الطعام","whatsapp_number":""}' > "$WS/08_rules/app_inputs.json"
python3 -I "$PLUG/skills/maestro-app-designer/scripts/build_app_data.py" "$WS" "$D" "$WS/14_app/$D/app_data.json" "$WS/08_rules/app_inputs.json"
python3 -I "$EX/check_rehearsal.py" "$PLUG" "$WS" "$D"
