#!/usr/bin/env python3
"""maestro-git-keeper: copy plugin + safe run outputs into a git clone, scrub, verify, commit.
Never deletes files in the repo. Push is done by the caller (needs session credentials).

usage: git_sync.py --plugin P --repo-dir R [--workspace W --run DATE] [--no-outputs] [--no-scrub] [--status S]
prints JSON {added, modified, unchanged, committed, sha, leaks}
"""
import argparse, json, os, re, shutil, subprocess, sys
from datetime import date

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w/])\+?\d[\d\s-]{8,}\d(?![\w/])")
SECRET = re.compile(r"\b(EAA[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|gh[ousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|xox[abp]-[A-Za-z0-9-]{10,})")
PRIV = re.compile(r"https?://(claude\.ai/(artifact|code)/\S+|drive\.google\.com/\S+|docs\.google\.com/\S+|[\w-]+\.monday\.com/\S+|meet\.google\.com/\S+)")
TEXT_EXT = {".md", ".txt", ".json", ".csv", ".py", ".sh", ".html", ".yml", ".yaml"}
SAFE_OUT_EXT = TEXT_EXT | {".docx", ".xlsx", ".pdf"}
EXCLUDE_NAME = re.compile(r"(people|contacts|recipients|emails?_log|sent_|mail_log|token|secret|\.env|credentials)", re.I)
SKIP_DIRS = {".git", "__pycache__", ".in_use", "node_modules"}
MAX = 20 * 1024 * 1024
# whitelisted dummy-data paths kept verbatim except scrubbing
def scrub(t):
    t = EMAIL.sub("user@example.com", t)
    t = SECRET.sub("[secret]", t)
    t = PRIV.sub("[private-link]", t)
    t = PHONE.sub(lambda m: m.group(0) if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", m.group(0)) or len(re.sub(r"\D", "", m.group(0))) > 15 else "[phone]", t)
    return t

def leaks(t):
    return len(EMAIL.findall(t)) + len(SECRET.findall(t)) + len(PRIV.findall(t))

def copy_tree(src, dst, stats, do_scrub, outputs=False):
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            s = os.path.join(dp, fn); ext = os.path.splitext(fn)[1].lower()
            pub_bad = outputs and do_scrub and (ext not in {".md", ".json"} or re.search(r"(mapping|rewards|tasks|matches|insights|partner|donor)", fn))
            if os.path.getsize(s) > MAX or pub_bad or (outputs and (ext not in SAFE_OUT_EXT or EXCLUDE_NAME.search(fn) or "/original" in s or "/raw" in s)):
                stats["excluded"] += 1; continue
            if not outputs and EXCLUDE_NAME.search(fn) and "examples" not in s:
                stats["excluded"] += 1; continue
            d = os.path.join(dst, os.path.relpath(s, src)); os.makedirs(os.path.dirname(d), exist_ok=True)
            if ext in TEXT_EXT:
                data = open(s, encoding="utf-8", errors="replace").read()
                if do_scrub: data = scrub(data)
                stats["leaks"] += leaks(data) if do_scrub else 0
                new = data.encode("utf-8")
            else:
                new = open(s, "rb").read()
            old = open(d, "rb").read() if os.path.exists(d) else None
            if old == new: stats["unchanged"] += 1; continue
            stats["modified" if old is not None else "added"] += 1
            open(d, "wb").write(new)

def sh(*a, cwd):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plugin", required=True); ap.add_argument("--repo-dir", required=True)
    ap.add_argument("--workspace"); ap.add_argument("--run", default=date.today().isoformat())
    ap.add_argument("--no-outputs", action="store_true"); ap.add_argument("--no-scrub", action="store_true")
    ap.add_argument("--status", default="done")
    A = ap.parse_args(); R = A.repo_dir
    before = int(sh("git", "ls-files", cwd=R).stdout.count("\n"))
    st = dict(added=0, modified=0, unchanged=0, excluded=0, leaks=0)
    copy_tree(A.plugin, os.path.join(R, "foodrescue-ai-maestro"), st, not A.no_scrub)
    if A.workspace and not A.no_outputs:
        # public repo (scrub on): plugin + run summaries + sourced market brief only (no partner/donor/staff names)
        subs = ["13_run_log", "09_market"] if not A.no_scrub else ["13_run_log", "01_data", "02_minutes", "03_reports", "06_tasks", "07_rewards", "09_market", "12_calendar"]
        for sub in subs:
            p = os.path.join(A.workspace, sub)
            if os.path.isdir(p):
                src = os.path.join(p, A.run) if os.path.isdir(os.path.join(p, A.run)) else p
                copy_tree(src, os.path.join(R, "runs", A.run, sub), st, not A.no_scrub, outputs=True)
    if st["leaks"]:
        print(json.dumps({**st, "committed": False, "error": "sensitive pattern left after scrub"})); sys.exit(2)
    if st["added"] or st["modified"]:
        cl = os.path.join(R, "CHANGELOG.md"); prev = open(cl, encoding="utf-8").read() if os.path.exists(cl) else "# سجل التغييرات\n\n"
        open(cl, "w", encoding="utf-8").write(prev + f"- {A.run} — تشغيل {A.status}: +{st['added']} ملف جديد، ~{st['modified']} معدّل\n")
    sh("git", "add", "-A", cwd=R)
    deleted = [l for l in sh("git", "diff", "--cached", "--name-status", cwd=R).stdout.splitlines() if l.startswith("D")]
    if deleted:
        print(json.dumps({**st, "committed": False, "error": "deletion detected", "deleted": deleted})); sys.exit(3)
    if not sh("git", "diff", "--cached", "--quiet", cwd=R).returncode:
        print(json.dumps({**st, "committed": False, "sha": None, "note": "no changes"})); return
    msg = f"FR {A.run} — run {A.status}: +{st['added']} ~{st['modified']}\n\nCo-Authored-By: Claude Opus 5.5 <user@example.com>"
    r = sh("git", "-c", "user.name=FoodRescue AI Maestro", "-c", "user.email=user@example.com", "commit", "-q", "-m", msg, cwd=R)
    sha = sh("git", "rev-parse", "--short", "HEAD", cwd=R).stdout.strip()
    after = int(sh("git", "ls-files", cwd=R).stdout.count("\n"))
    print(json.dumps({**st, "committed": r.returncode == 0, "sha": sha, "files_before": before, "files_after": after}))

if __name__ == "__main__":
    main()
