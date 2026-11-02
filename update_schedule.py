"""Sync UFC schedule from ESPN into events.json. Numbered events show as 'UFC 320'; Fight Nights keep ESPN's title."""
import json, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

URL = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard?dates={s}-{e}&limit=200"

def clean(ev):
    m = re.search(r"UFC\s+(\d{3})\b", ev.get("name", ""), re.I)
    d = datetime.fromisoformat(ev["date"].replace("Z", "+00:00")) - timedelta(hours=6)
    return {"id": str(ev["id"]), "title": f"UFC {m.group(1)}" if m else (ev.get("name") or "UFC Fight Night"),
            "date": d.strftime("%Y-%m-%d"), "type": "ppv" if m else "fn"}

def fetch(s, e):
    req = urllib.request.Request(URL.format(s=s, e=e), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("events", [])

now = datetime.now(timezone.utc)
start = datetime(2025, 1, 1, tzinfo=timezone.utc)
end = now + timedelta(days=180)
found, errors = {}, 0
cur = start
while cur < end:  # one request per ~month; long ranges can get truncated
    nxt = min(cur + timedelta(days=30), end)
    try:
        for ev in fetch(cur.strftime("%Y%m%d"), nxt.strftime("%Y%m%d")):
            c = clean(ev); found[c["id"]] = c
    except Exception as ex:
        errors += 1
        print(f"Request {cur:%Y-%m-%d} failed: {ex!r}", file=sys.stderr)
    cur = nxt + timedelta(days=1)

print(f"{len(found)} events, {errors} failed requests")
if not found:
    sys.exit("ESPN returned no events; leaving events.json unchanged")
with open("events.json", "w") as f:
    json.dump(sorted(found.values(), key=lambda e: (e["date"], e["id"])), f, indent=1)
