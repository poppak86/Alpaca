import json
from pathlib import Path
from datetime import datetime, timedelta

ACCOUNT_FILE = "account_balance.json"


def load_account():
    """Load account data from disk or initialize it the first time."""
    if Path(ACCOUNT_FILE).exists():
        with open(ACCOUNT_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {
            "cash": 700.0,
            "pending_settlements": [],
            "positions": {},
        }
        save_account(data)
    return data


def save_account(data):
    with open(ACCOUNT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def process_settlements(data):
    """Release pending settlements if their release date has passed."""
    today = datetime.utcnow().date()
    remaining = []
    for p in data.get("pending_settlements", []):
        release = datetime.fromisoformat(p["release_date"]).date()
        if release <= today:
            data["cash"] += p["amount"]
        else:
            remaining.append(p)
    data["pending_settlements"] = remaining
    return data


def deduct_cash(data, amount):
    if data.get("cash", 0) >= amount:
        data["cash"] -= amount
        return True
    return False


def add_pending_settlement(data, amount):
    release_date = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
    data.setdefault("pending_settlements", []).append({
        "amount": amount,
        "release_date": release_date,
    })
    return data


def add_position(data, symbol, qty):
    positions = data.setdefault("positions", {})
    positions[symbol] = positions.get(symbol, 0) + qty
    return data


def remove_position(data, symbol, qty):
    positions = data.setdefault("positions", {})
    current = positions.get(symbol, 0)
    if qty >= current:
        positions.pop(symbol, None)
    else:
        positions[symbol] = current - qty
    return data
