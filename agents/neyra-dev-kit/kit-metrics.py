#!/usr/bin/env python3
"""Kit performance metrics — the kit measuring itself.

Deterministic sources only (no model self-reporting):
  .neyra/kit-metrics.jsonl   hook telemetry: subagent launches, stop-gate
                             results, guard blocks (local, gitignored)
  agents/neyra-dev-kit/signals.log   captured kit-evolution insights
  git log                    VERSION bumps (evolution velocity)
  .neyra-kit-canonical / .neyra-dev-kit.source   source ownership mode

Usage: kit-metrics.py [repo-root] [--days N]
"""

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_args(argv):
    root, days = ".", 30
    it = iter(argv)
    for a in it:
        if a == "--days":
            days = int(next(it, "30"))
        else:
            root = a
    return Path(root).resolve(), days


def load_events(root, since):
    p = root / ".neyra" / "kit-metrics.jsonl"
    events = []
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
                ts = datetime.fromisoformat(e.get("ts", "").replace("Z", "+00:00"))
                if ts >= since:
                    events.append(e)
            except (ValueError, KeyError):
                continue
    return events


def load_signals(root, since):
    p = root / "agents" / "neyra-dev-kit" / "signals.log"
    rows = []
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or "|" not in line:
                continue
            parts = [c.strip() for c in line.split("|")]
            if len(parts) < 4:
                continue
            try:
                d = datetime.strptime(parts[0], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if d >= since:
                rows.append(
                    {
                        "date": parts[0],
                        "signal": parts[1],
                        "route": parts[2],
                        "kind": parts[3],
                    }
                )
    return rows


def version_bumps(root, days):
    try:
        out = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "log",
                f"--since={days} days ago",
                "--format=%h %ad %s",
                "--date=short",
                "--",
                "agents/neyra-dev-kit/VERSION",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout.strip()
        return [ln for ln in out.splitlines() if ln]
    except Exception:
        return []


def main(argv):
    root, days = parse_args(argv)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    print(f"kit-metrics — {root.name}, last {days}d")

    events = load_events(root, since)
    launches = Counter(
        e.get("type", "unknown") for e in events if e.get("event") == "subagent_launch"
    )
    gates = Counter(
        e.get("result", "?") for e in events if e.get("event") == "stop_gate"
    )
    blocks = [e.get("path", "?") for e in events if e.get("event") == "guard_block"]

    print("\n── subagent launches (hook-counted)")
    if launches:
        for name, n in launches.most_common(15):
            print(f"  {n:4d}  {name}")
        print(f"  total: {sum(launches.values())} across {len(launches)} types")
    else:
        print("  no data yet — counts appear as the Task hook observes launches")

    print("\n── gates")
    total_gates = sum(gates.values())
    if total_gates:
        blocked = gates.get("blocked", 0)
        print(
            f"  stop-gate: {total_gates} runs, {blocked} blocked ({100 * blocked // total_gates}%)"
        )
    else:
        print("  stop-gate: no data yet")
    print(
        f"  guard blocks (kit-managed file edits denied): {len(blocks)}"
        + (f" — latest: {blocks[-1]}" if blocks else "")
    )

    sig = load_signals(root, since)
    print(f"\n── evolution signals (signals.log, {len(sig)} in window)")
    if sig:
        kinds = Counter(s["kind"] for s in sig)
        print("  " + ", ".join(f"{k}: {n}" for k, n in kinds.most_common()))
        shipped = sum(
            1 for s in sig if re.search(r"shipped|this change", s["route"], re.I)
        )
        print(f"  routed-to-shipped ratio (rough): {shipped}/{len(sig)}")
        for s in sig[-3:]:
            print(f"  · {s['date']} [{s['kind']}] {s['signal'][:80]}")

    bumps = version_bumps(root, days)
    print(f"\n── evolution velocity: {len(bumps)} VERSION bump(s) in {days}d")
    for b in bumps[:5]:
        print(f"  {b}")

    ver_file = root / "agents" / "neyra-dev-kit" / "VERSION"
    version = ver_file.read_text().strip() if ver_file.is_file() else "?"
    if (root / ".neyra-kit-canonical").is_file():
        source_mode = "canonical authoring source"
    elif (root / ".neyra-dev-kit.source").is_file():
        source_mode = "consumer install"
    else:
        source_mode = "unstamped checkout"
    print(f"\n── source: {source_mode}, kit v{version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
