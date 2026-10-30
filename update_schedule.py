import json
import os
import urllib.request

FILENAME = "events.json"
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"

def fetch_espn_events():
    events_list = []
    try:
        req = urllib.request.Request(
            ESPN_URL,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            raw_events = data.get('events', [])
            
            for ev in raw_events:
                event_id = str(ev.get('id', ''))
                name = ev.get('name', 'UFC Event')
                date_str = ev.get('date', '')[:10]
                
                ev_type = "ppv" if any(num in name.lower() for num in ["ufc 3", "ufc 4", "ufc 5", "ufc 6", "ufc 7", "ufc 8", "ufc 9"]) or "ppv" in name.lower() else "fn"
                
                if event_id and date_str:
                    events_list.append({
                        "id": f"espn-{event_id}",
                        "title": name,
                        "date": date_str,
                        "type": ev_type
                    })
    except Exception as e:
        print(f"Error fetching from ESPN API: {e}")
    
    return events_list

def main():
    existing_events = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            try:
                existing_events = json.load(f)
            except:
                existing_events = []

    fetched = fetch_espn_events()
    
    if fetched:
        existing_ids = {e['id'] for e in existing_events}
        new_added = 0
        for ev in fetched:
            if ev['id'] not in existing_ids:
                existing_events.append(ev)
                new_added += 1
        
        existing_events.sort(key=lambda x: x.get('date', '9999-99-99'))
        
        with open(FILENAME, "w") as f:
            json.dump(existing_events, f, indent=4)
        print(f"Successfully updated schedule. Added {new_added} new events.")
    else:
        print("No events fetched from API or API unavailable. Keeping existing schedule.")

if __name__ == "__main__":
    ma
  in()
