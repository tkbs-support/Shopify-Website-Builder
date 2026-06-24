"""Fetch the live homepage and report every JSON-LD entity, hours, and key theme markers."""
import sys
import re
import json
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

html = ""
for attempt in range(4):
    try:
        req = urllib.request.Request("https://theclothingcove.com/",
                                     headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req).read().decode("utf-8", "replace")
        break
    except Exception as e:
        print("retry", attempt + 1, type(e).__name__)
        time.sleep(2)

blocks = re.findall(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", html, re.S)
print("JSON-LD blocks on live homepage:", len(blocks))
for b in blocks:
    try:
        d = json.loads(b)
        items = d if isinstance(d, list) else [d]
        for it in items:
            t = it.get("@type")
            nap = bool(it.get("telephone") or it.get("address"))
            same = len(it.get("sameAs", []))
            hrs = ""
            for h in it.get("openingHoursSpecification", []):
                day = h.get("dayOfWeek")
                day = day if isinstance(day, list) else [day]
                names = ",".join(str(x).split("/")[-1][:3] for x in day)
                hrs += " {} {}-{};".format(names, h.get("opens"), h.get("closes"))
            print("  type={} NAP={} sameAs={} hours:{}".format(t, nap, same, hrs or " none"))
    except Exception:
        print("  unparseable:", str(b).strip()[:60])

print()
print("Hidden keyword H1 present:", "The Clothing Cove — Women's Clothing, Dresses" in html
      or "u-visually-hidden" in html)
m = re.search(r"<title>\s*(.{0,100})", html)
print("Title:", m.group(1).strip()[:95] if m else "none")
print("Milford content section:", "Women's Clothing & Accessories in Milford, MI" in html)
print("New banner DESKTOP_25:", "Website_Banners_DESKTOP_25" in html)
