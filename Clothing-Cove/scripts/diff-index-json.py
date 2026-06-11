"""Structural diff of templates/index.json: live vs tkbs."""
import json

live = json.load(open("data/themes/live/files/templates/index.json", encoding="utf-8"))
tkbs = json.load(open("data/themes/tkbs/files/templates/index.json", encoding="utf-8"))

ls, ts = live["sections"], tkbs["sections"]

print("=== Section order ===")
print("live:", live["order"])
print("tkbs:", tkbs["order"])

print("\n=== Sections only in live ===")
for sid in ls:
    if sid not in ts:
        print(f"--- {sid} ({ls[sid].get('type')}) ---")
        print(json.dumps(ls[sid], indent=1)[:2000])

print("\n=== Sections only in tkbs ===")
for sid in ts:
    if sid not in ls:
        print(f"--- {sid} ({ts[sid].get('type')}) ---")
        print(json.dumps(ts[sid], indent=1)[:2000])

print("\n=== Sections in both but different ===")
for sid in ls:
    if sid in ts and ls[sid] != ts[sid]:
        print(f"--- {sid} ({ls[sid].get('type')}) ---")
        a = json.dumps(ls[sid], indent=1, sort_keys=True).splitlines()
        b = json.dumps(ts[sid], indent=1, sort_keys=True).splitlines()
        import difflib
        for line in difflib.unified_diff(b, a, "tkbs", "live", lineterm=""):
            print(line)
