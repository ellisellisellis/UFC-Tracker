import json
import os
import urllib.request
import datetime

FILENAME = "events.json"

def fetch_espn_for_month(year_month):
    """Fetch UFC events from ESPN for a specific YYYYMM format."""
    events_list = []
    url = f"https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard?dates={year_month}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            raw_events = data.get('events', [])
            
            for ev in raw_events:
                event_id = str(ev.get('id', ''))
                name = ev.get('name', 'UFC Event')
                date_str = ev.get('date', '')[:10]
                
                # Tag as PPV Main Event or Fight Night
                ev_type = "ppv" if any(k in name.lower() for k in ["ufc 3", "ufc 4", "ufc 5", "ufc 6", "ufc 7", "ufc 8", "ufc 9"]) or "ppv" in name.lower() else "fn"
                
                if event_id and date_str:
                    events_list.append({
                        "id": f"espn-{event_id}",
                        "title": name,
                        "date": date_str,
                        "type": ev_type
                    })
    except Exception as e:
        print(f"Error fetching for {year_month}: {e}")
    
    return events_list

def main():
    existing_events = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            try:
                existing_events = json.load(f)
            except:
                existing_events = []

    now = datetime.datetime.now()
    months_to_check = []
    
    # Range -3 to +3: Fetches the last 3 months of events plus upcoming events
    for i in range(-3, 4):
        m = (now.month - 1 + i) % 12 + 1
        y = now.year + (now.month - 1 + i) // 12
        months_to_check.append(f"{y}{m:02d}")

    all_fetched = []
    for ym in months_to_check:
        all_fetched.extend(fetch_espn_for_month(ym))

    if all_fetched:
        existing_ids = {e['id'] for e in existing_events}
        new_added = 0
        for ev in all_fetched:
            if ev['id'] not in existing_ids:
                existing_events.append(ev)
                new_added += 1
        
        # Sort chronologically (oldest first)
        existing_events.sort(key=lambda x: x.get('date', '9999-99-99'))
        
        with open(FILENAME, "w") as f:
            json.dump(existing_events, f, indent=4)
        print(f"Schedule updated! Added {new_added} new events. Total events: {len(existing_events)}")
    else:
        print("No events fetched.")

if __name__ == "__main__":
   
    main()
