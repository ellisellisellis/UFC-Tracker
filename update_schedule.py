"""Sync UFC schedule from ESPN into events.json. Titles are stripped of fighter names."""
import json, re, urllib.request
from datetime import datetime, timedelta, timezone

URL = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard?dates={s}-{e}&limit=500"

def clean(ev):
    m = re.search(r"UFC\s+(\d{3})\b", ev.get("name", ""), re.I)
    d = datetime.fromisoformat(ev["date"].replace("Z", "+00:00")) - timedelta(hours=6)
    return {"id": str(ev["id"]), "title": f"UFC {m.group(1)}" if m else "UFC Fight Night",
            "date": d.strftime("%Y-%m-%d"), "type": "ppv" if m else "fn"}

now = datetime.now(timezone.utc)
url = URL.format(s=f"{now.year-1}0101", e=(now + timedelta(days=180)).strftime("%Y%m%d"))
with urllib.request.urlopen(url, timeout=30) as r:
    events = [clean(e) for e in json.load(r).get("events", [])]
if not events:
    raise SystemExit("ESPN returned no events; leaving events.json unchanged")
events.sort(key=lambda e: (e["date"], e["id"]))
with open("events.json", "w") as f:
    json.dump(events, f, indent=1)
print(f"Wrote {len(events)} events")
