import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import requests

BLOCKLIST_FILE = "econ_blocklist.json"
FMP_API_KEY = os.getenv("FMP_API_KEY", "demo")

API_URL = "https://financialmodelingprep.com/api/v4/economic_calendar"

KEYWORDS = ["fed", "fomc", "cpi", "earnings"]

def fetch_events(start: datetime, end: datetime) -> List[Dict]:
    params = {
        "from": start.strftime("%Y-%m-%d"),
        "to": end.strftime("%Y-%m-%d"),
        "apikey": FMP_API_KEY,
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Failed to fetch economic events: {e}")
        return []


def update_blocklist(days: int = 7) -> List[Dict]:
    start = datetime.utcnow().date()
    end = start + timedelta(days=days)
    events = fetch_events(start, end)
    blocked = []
    for ev in events:
        name = str(ev.get("event", "")).lower()
        if any(k in name for k in KEYWORDS):
            date_str = ev.get("date")
            if not date_str:
                continue
            try:
                ts = datetime.fromisoformat(date_str)
            except ValueError:
                # Some APIs use date & time fields
                try:
                    ts = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue
            blocked.append({"event": ev.get("event"), "time": ts.isoformat()})
    if blocked:
        with open(BLOCKLIST_FILE, "w") as f:
            json.dump(blocked, f, indent=2)
    return blocked


def is_blocked_now() -> Tuple[bool, str]:
    if not os.path.exists(BLOCKLIST_FILE):
        return False, ""
    now = datetime.utcnow()
    try:
        with open(BLOCKLIST_FILE) as f:
            events = json.load(f)
    except Exception:
        return False, ""
    for ev in events:
        try:
            ts = datetime.fromisoformat(ev["time"])
        except Exception:
            continue
        if abs((now - ts).total_seconds()) < 3600:
            return True, ev.get("event", "")
    return False, ""

if __name__ == "__main__":
    # update blocklist when run directly
    updated = update_blocklist()
    print(f"Updated blocklist with {len(updated)} events")
