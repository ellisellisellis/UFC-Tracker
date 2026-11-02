import json
import os
import urllib.request
import datetime

FILENAME = "events.json"

def fetch_espn_scoreboard():
    """Fetch active and upcoming UFC events from ESPN default scoreboard."""
    events_list = []
    url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            raw_events = data.get('events', [])
            
            for ev in raw_events:
                event_id = str(ev.get('id', ''))
                name = ev.get('name', 'UFC Event')
                date_str = ev.get('date', '')[:10]
                
                ev_type = "ppv" if any(k in name.lower() for k in ["ufc 3", "ufc 4", "ufc 5", "ufc 6", "ufc 7", "ufc 8", "ufc 9"]) or "ppv" in name.lower() else "fn"
                
                if event_id and date_str:
                    events_list.append({
                        "id": f"espn-{event_id}",
                        "title": name,
                        "date": date_str,
                        "type": ev_type
                    })
    except Exception as e:
        print(f"Note: Could not fetch ESPN scoreboard: {e}")
    
    return events_list

def main():
    try:
        existing_events = []
        if os.path.exists(FILENAME):
            with open(FILENAME, "r") as f:
                try:
                    existing_events = json.load(f)
                except:
                    existing_events = []

        fetched = fetch_espn_scoreboard()

        if fetched:
            existing_ids = {e['id'] for e in existing_events}
            new_added = 0
            for ev in fetched:
                if ev['id'] not in existing_ids:
                    existing_events.append(ev)
                    new_added += 1
            
            # Sort chronologically (oldest first)
            existing_events.sort(key=lambda x: x.get('date', '9999-99-99'))
            
            with open(FILENAME, "w") as f:
                json.dump(existing_events, f, indent=4)
            print(f"Schedule updated! Added {new_added} new events. Total events: {len(existing_events)}")
        else:
            print("No new events fetched from API, keeping existing schedule intact.")
            
    except Exception as e:
        print(f"Safe exit from script error: {e}")

if __name__ == "__main__":
    
    main()
