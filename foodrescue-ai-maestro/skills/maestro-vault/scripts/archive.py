#!/usr/bin/env python3
"""maestro-vault: copy (never move/delete) every run output into the standard folders with
FR_<date>_<agent>_<topic>.<ext> naming; resolve conflicts with _v2.._vN; write archive_index.json.

usage: archive.py <workspace> <run_date> <manifest.json>
"""
import sys, json, os, shutil, re

FOLDER = {"excel": "01_data/cleaned", "data": "01_data/cleaned", "minutes": "02_minutes/final", "tasks": "06_tasks",
          "report": "03_reports", "post": "04_posts", "card": "07_rewards", "deck": "05_decks", "video": "10_video",
          "email": "11_mail", "invite": "12_calendar", "market": "09_market", "archive": "13_run_log"}

def slug(s):
    return re.sub(r"[^\w\-]+", "-", s, flags=re.UNICODE).strip("-").lower()[:40] or "file"

def main():
    ws, run, mf = sys.argv[1:4]
    M = json.load(open(mf)); idx = []
    for a in M.get("agents", []):
        short = a["agent"].replace("maestro-", "")
        for o in a.get("outputs", []):
            src = o.get("path") and os.path.join(ws, o["path"])
            if not src or not os.path.exists(src):
                idx.append({**o, "agent": a["agent"], "archived": None, "note": "رابط خارجي فقط" if o.get("url") else "الملف غير موجود"}); continue
            base, ext = os.path.splitext(os.path.basename(src))
            name = base if base.startswith(f"FR_{run}_") else f"FR_{run}_{short}_{slug(o.get('topic') or base)}"
            dest_dir = os.path.join(ws, FOLDER.get(o.get("kind"), "13_run_log"), run); os.makedirs(dest_dir, exist_ok=True)
            dest, v = os.path.join(dest_dir, name + ext), 2
            while os.path.exists(dest):
                dest = os.path.join(dest_dir, f"{name}_v{v}{ext}"); v += 1
            shutil.copy2(src, dest)
            idx.append({**o, "agent": a["agent"], "archived": os.path.relpath(dest, ws)})
    out = os.path.join(ws, "13_run_log", run, "archive_index.json"); os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"run": run, "items": idx}, open(out, "w"), ensure_ascii=False, indent=2)
    print(json.dumps({"archived": sum(1 for i in idx if i.get("archived")), "external": sum(1 for i in idx if not i.get("archived"))}, ensure_ascii=False))

if __name__ == "__main__":
    main()
