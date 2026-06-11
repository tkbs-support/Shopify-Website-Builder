"""Post-capture checks: live assets touched since the TKBS copy, byte-compare pairs."""
import json
import hashlib
import os
from datetime import datetime

COPY_MOMENT = datetime.fromisoformat("2026-05-15T15:22:20-04:00")

live = json.load(open("data/themes/live/asset_list.json"))
tkbs = {a["key"]: a for a in json.load(open("data/themes/tkbs/asset_list.json"))}

print("Live assets touched after the TKBS copy was created:")
for a in live:
    if datetime.fromisoformat(a["updated_at"]) > COPY_MOMENT:
        same = tkbs[a["key"]]["checksum"] == a["checksum"]
        print(f"  {a['key']}  updated {a['updated_at']}  content-identical-to-tkbs: {same}")

print("\nByte-compare downloaded pairs:")
for key in ["assets/AB.png", "assets/Honey.png", "assets/theme.scss"]:
    p1 = os.path.join("data/themes/live/files", *key.split("/"))
    p2 = os.path.join("data/themes/tkbs/files", *key.split("/"))
    h1 = hashlib.md5(open(p1, "rb").read()).hexdigest()
    h2 = hashlib.md5(open(p2, "rb").read()).hexdigest()
    print(f"  {key}: live {os.path.getsize(p1)}B vs tkbs {os.path.getsize(p2)}B, same bytes: {h1 == h2}")
