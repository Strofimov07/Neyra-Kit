#!/usr/bin/env python3
"""tracker-queue.py — a replayable queue of tracker mutations for when the tracker is down (NEB-1669).

A consumer lost its tracker for seven days. Closures were finished locally, an audit
result was typed into a free-form handoff note, and nothing reminded the next session —
the prose fallback the bootstrap named did not even exist on disk. Intended mutations
now go into one file, one JSON object per line, that a script can list and that the
session-start bootstrap reports (count + age) until it is empty. The replay itself is
done by the agent through the tracker connector — this script holds the intent, not the
credentials.

Usage (root = $CLAUDE_PROJECT_DIR, else cwd; files live in <root>/.neyra/):
  tracker-queue.py add --issue NEB-123 --op comment --text "…" [--reason "…"]
  tracker-queue.py add --issue NEB-123 --op state   --state Done [--text "closing note"]
  tracker-queue.py add --op create --project "Neyra Skills Kit" --title "…" --text "…"
  tracker-queue.py list             # oldest first, with age
  tracker-queue.py status           # one line for hooks/doctor, empty when the queue is empty
  tracker-queue.py done <n> | --all # mark replayed (moved to tracker-queue.done.jsonl)
Pure stdlib.
"""
import argparse
import json
import os
import sys
import time

QUEUE = "tracker-queue.jsonl"
DONE = "tracker-queue.done.jsonl"


def root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def path(name):
    return os.path.join(root(), ".neyra", name)


def load():
    p = path(QUEUE)
    if not os.path.isfile(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def save(entries, name=QUEUE, mode="w"):
    os.makedirs(os.path.dirname(path(name)), exist_ok=True)
    with open(path(name), mode, encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")


def age_days(ts):
    try:
        return int((time.time() - time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))) // 86400)
    except ValueError:
        return 0


def cmd_add(a):
    if a.op in ("comment", "state") and not a.issue:
        sys.exit("tracker-queue: --issue is required for op=%s" % a.op)
    if a.op == "state" and not a.state:
        sys.exit("tracker-queue: --state is required for op=state")
    if a.op == "create" and not (a.title and a.project):
        sys.exit("tracker-queue: --title and --project are required for op=create")
    entries = load()
    n = (max((e.get("n", 0) for e in entries), default=0)) + 1
    entry = {
        "n": n,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "op": a.op,
        "issue": a.issue,
        "state": a.state,
        "project": a.project,
        "title": a.title,
        "text": a.text,
        "reason": a.reason or "tracker unavailable",
    }
    save([entry], mode="a")
    print("queued #%d: %s %s%s" % (n, a.op, a.issue or a.title or "", " → " + a.state if a.state else ""))
    return 0


def describe(e):
    what = {"comment": "comment on %s" % e.get("issue"),
            "state": "%s → %s" % (e.get("issue"), e.get("state")),
            "create": "create in %s: %s" % (e.get("project"), e.get("title"))}.get(e.get("op"), e.get("op"))
    return "#%d  %s  (%dd ago, %s)" % (e.get("n", 0), what, age_days(e.get("ts", "")), e.get("reason", ""))


def cmd_list(_a):
    entries = load()
    if not entries:
        print("tracker queue empty")
        return 0
    print("%d queued tracker mutation(s) — replay through the tracker connector, then `done <n>`:" % len(entries))
    for e in entries:
        print("  " + describe(e))
        if e.get("text"):
            print("      " + e["text"].replace("\n", "\n      ")[:400])
    return 0


def cmd_status(_a):
    entries = load()
    if not entries:
        return 0
    oldest = max(age_days(e.get("ts", "")) for e in entries)
    print("%d queued tracker mutation(s) in .neyra/tracker-queue.jsonl, oldest %dd — replay before new work: python3 agents/neyra-dev-kit/tracker-queue.py list"
          % (len(entries), oldest))
    return 0


def cmd_done(a):
    entries = load()
    if a.all:
        moved, keep = entries, []
    else:
        if a.n is None:
            sys.exit("tracker-queue: done needs an entry number or --all")
        n = int(a.n)
        moved = [e for e in entries if e.get("n") == n]
        keep = [e for e in entries if e.get("n") != n]
        if not moved:
            sys.exit("tracker-queue: no entry #%d" % n)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for e in moved:
        e["done_at"] = stamp
    save(moved, DONE, mode="a")
    save(keep)
    print("marked done: %s (%d left)" % (", ".join("#%d" % e.get("n", 0) for e in moved) or "nothing", len(keep)))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog="tracker-queue.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("--op", choices=("comment", "state", "create"), required=True)
    add.add_argument("--issue")
    add.add_argument("--state")
    add.add_argument("--project")
    add.add_argument("--title")
    add.add_argument("--text", default="")
    add.add_argument("--reason")
    add.set_defaults(fn=cmd_add)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    done = sub.add_parser("done")
    done.add_argument("n", nargs="?", help="entry number")
    done.add_argument("--all", action="store_true", help="mark every queued entry replayed")
    done.set_defaults(fn=cmd_done)
    a = ap.parse_args(argv[1:])
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
