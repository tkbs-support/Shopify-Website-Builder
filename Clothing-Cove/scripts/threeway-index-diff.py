"""3-way attribution for templates/index.json.

ancestor = data/theme/templates__index.json (live theme, fetched 2026-06-10 14:09,
           before the client's 14:56 edit; live had no other edits since the
           2026-05-15 TKBS copy, so this equals the copy-time state)
live     = data/themes/live/files/templates/index.json (after client edit)
tkbs     = data/themes/tkbs/files/templates/index.json (after Josh's edits)
"""
import json

anc = json.load(open("data/theme/templates__index.json", encoding="utf-8"))
live = json.load(open("data/themes/live/files/templates/index.json", encoding="utf-8"))
tkbs = json.load(open("data/themes/tkbs/files/templates/index.json", encoding="utf-8"))


def leaves(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(leaves(v, f"{prefix}.{k}" if prefix else k))
    else:
        out[prefix] = obj
    return out


a, l, t = leaves(anc), leaves(live), leaves(tkbs)
paths = sorted(set(a) | set(l) | set(t))

client_changes, josh_changes, conflicts, both_same = [], [], [], []
MISSING = object()
for p in paths:
    av, lv, tv = a.get(p, MISSING), l.get(p, MISSING), t.get(p, MISSING)
    if lv == av and tv == av:
        continue
    if lv != av and tv == av:
        client_changes.append((p, av, lv))
    elif tv != av and lv == av:
        josh_changes.append((p, av, tv))
    elif lv == tv:
        both_same.append((p, av, lv))
    else:
        conflicts.append((p, av, lv, tv))


def show(val):
    s = json.dumps(val if val is not MISSING else "<absent>", ensure_ascii=False)
    return s if len(s) <= 120 else s[:117] + "..."


print(f"=== CLIENT changes (live-only, June 10) — {len(client_changes)} ===")
for p, av, lv in client_changes:
    print(f" {p}\n   was:  {show(av)}\n   now:  {show(lv)}")

print(f"\n=== JOSH changes (tkbs-only, May 15-18) — {len(josh_changes)} ===")
for p, av, tv in josh_changes:
    print(f" {p}\n   was:  {show(av)}\n   tkbs: {show(tv)}")

print(f"\n=== TRUE CONFLICTS (both changed same setting) — {len(conflicts)} ===")
for p, av, lv, tv in conflicts:
    print(f" {p}\n   ancestor: {show(av)}\n   live:     {show(lv)}\n   tkbs:     {show(tv)}")

print(f"\n=== Both changed identically — {len(both_same)} ===")
for p, av, v in both_same:
    print(f" {p}: {show(av)} -> {show(v)}")

print("\n=== Section order ===")
print("ancestor:", anc["order"])
print("live:    ", live["order"])
print("tkbs:    ", tkbs["order"])
