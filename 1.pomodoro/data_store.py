"""
data_store.py - JSON-based persistence for the Pomodoro timer.

Stores total pomodoros, XP, level, streak, badges, and daily history.
"""

import json
import os
from datetime import date
from typing import Any, Dict

DATA_FILE = os.path.join(os.path.dirname(__file__), "pomodoro_data.json")

DEFAULT_DATA: Dict[str, Any] = {
    "total_pomodoros": 0,
    "xp": 0,
    "level": 1,
    "streak": {
        "current": 0,
        "longest": 0,
        "last_date": None,
    },
    "badges": [],
    "history": [],  # list of {"date": "YYYY-MM-DD", "pomodoros": int, "focus_minutes": int}
}


def load_data() -> Dict[str, Any]:
    """Load data from the JSON file, or return defaults if not found."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Back-fill any missing keys from DEFAULT_DATA
        for key, value in DEFAULT_DATA.items():
            if key not in data:
                data[key] = value
        if "streak" not in data or not isinstance(data["streak"], dict):
            data["streak"] = DEFAULT_DATA["streak"].copy()
        return data
    return {
        k: (v.copy() if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
        for k, v in DEFAULT_DATA.items()
    }


def save_data(data: Dict[str, Any]) -> None:
    """Persist data to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_pomodoro_session(data: Dict[str, Any], focus_minutes: int = 25) -> None:
    """Increment today's pomodoro count and total count in *data* (in-place)."""
    today = date.today().isoformat()
    history = data.setdefault("history", [])
    for entry in history:
        if entry["date"] == today:
            entry["pomodoros"] += 1
            entry["focus_minutes"] += focus_minutes
            break
    else:
        history.append({"date": today, "pomodoros": 1, "focus_minutes": focus_minutes})
    data["total_pomodoros"] = data.get("total_pomodoros", 0) + 1
