"""Capture the delta between the live theme and the TKBS theme.

Phase 1-2 of the port plan (read-only):
- Fetch full asset lists (with checksums) for both themes
- Compare by checksum, download every differing/added/removed asset
- Classify by updated_at against the TKBS copy creation moment
- Write data/themes/delta-summary.json for the report
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"

LIVE_ID = "138024386675"   # Prestige update theme-sc 02-07-2025 (published)
TKBS_ID = "145504469107"   # Prestige Updates TKBS - 05-15-2026

# Moment the TKBS copy was created (theme created_at)
COPY_MOMENT = datetime.fromisoformat("2026-05-15T15:22:20-04:00")

OUT = "data/themes"


def api_get(url):
    for attempt in range(6):
        req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = float(e.headers.get("Retry-After", 2))
                time.sleep(wait)
                continue
            raise
    raise RuntimeError(f"Rate-limited too many times: {url}")


def fetch_asset_list(theme_id):
    url = f"https://{STORE}/admin/api/{API_VERSION}/themes/{theme_id}/assets.json"
    return api_get(url)["assets"]


def fetch_asset(theme_id, key):
    url = (f"https://{STORE}/admin/api/{API_VERSION}/themes/{theme_id}"
           f"/assets.json?asset%5Bkey%5D={urllib.parse.quote(key, safe='')}")
    return api_get(url)["asset"]


def save_asset(side, asset):
    """Write asset content under data/themes/<side>/files/<key>."""
    key = asset["key"]
    path = os.path.join(OUT, side, "files", key.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if asset.get("value") is not None:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(asset["value"])
    elif asset.get("attachment"):
        import base64
        with open(path, "wb") as f:
            f.write(base64.b64decode(asset["attachment"]))
    return path


def changed_since_copy(entry):
    return datetime.fromisoformat(entry["updated_at"]) > COPY_MOMENT


def main():
    os.makedirs(OUT, exist_ok=True)

    print("Fetching asset lists...")
    live_list = fetch_asset_list(LIVE_ID)
    tkbs_list = fetch_asset_list(TKBS_ID)
    for side, lst in (("live", live_list), ("tkbs", tkbs_list)):
        os.makedirs(os.path.join(OUT, side), exist_ok=True)
        with open(os.path.join(OUT, side, "asset_list.json"), "w", encoding="utf-8") as f:
            json.dump(lst, f, indent=1)
    print(f"  live: {len(live_list)} assets, tkbs: {len(tkbs_list)} assets")

    live = {a["key"]: a for a in live_list}
    tkbs = {a["key"]: a for a in tkbs_list}

    differing, live_only, tkbs_only, null_checksum = [], [], [], []
    for key, la in live.items():
        ta = tkbs.get(key)
        if ta is None:
            live_only.append(key)
        elif la.get("checksum") and ta.get("checksum"):
            if la["checksum"] != ta["checksum"]:
                differing.append(key)
        else:
            null_checksum.append(key)  # can't compare cheaply; download both
    for key in tkbs:
        if key not in live:
            tkbs_only.append(key)

    print(f"  differing: {len(differing)}, live-only: {len(live_only)}, "
          f"tkbs-only: {len(tkbs_only)}, null-checksum: {len(null_checksum)}")

    # Download content for everything we need to inspect
    to_fetch_live = sorted(differing + live_only + null_checksum)
    to_fetch_tkbs = sorted(differing + tkbs_only + null_checksum)
    for side, theme_id, keys in (("live", LIVE_ID, to_fetch_live),
                                 ("tkbs", TKBS_ID, to_fetch_tkbs)):
        print(f"Downloading {len(keys)} assets from {side}...")
        for i, key in enumerate(keys, 1):
            asset = fetch_asset(theme_id, key)
            save_asset(side, asset)
            if i % 20 == 0:
                print(f"  {i}/{len(keys)}")
            time.sleep(0.55)

    summary = {
        "copy_moment": COPY_MOMENT.isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "counts": {"live": len(live_list), "tkbs": len(tkbs_list)},
        "differing": [
            {
                "key": k,
                "live_updated_at": live[k]["updated_at"],
                "tkbs_updated_at": tkbs[k]["updated_at"],
                "live_changed_since_copy": changed_since_copy(live[k]),
                "tkbs_changed_since_copy": changed_since_copy(tkbs[k]),
            }
            for k in sorted(differing)
        ],
        "live_only": [
            {"key": k, "live_updated_at": live[k]["updated_at"],
             "live_created_at": live[k]["created_at"]}
            for k in sorted(live_only)
        ],
        "tkbs_only": [
            {"key": k, "tkbs_updated_at": tkbs[k]["updated_at"],
             "tkbs_created_at": tkbs[k]["created_at"]}
            for k in sorted(tkbs_only)
        ],
        "null_checksum": sorted(null_checksum),
    }
    with open(os.path.join(OUT, "delta-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print("Wrote data/themes/delta-summary.json")


if __name__ == "__main__":
    main()
