"""
gamification.py - XP/level system, achievement badges, and streak tracking.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

XP_PER_POMODORO = 10
_XP_BASE = 100  # XP needed to reach next level: level * _XP_BASE


# ---------------------------------------------------------------------------
# Badge definitions
# Each badge has:
#   id          - unique string key (stored in data["badges"])
#   name        - display name (emoji included)
#   description - tooltip / explanation
#   condition   - callable(data) -> bool
# ---------------------------------------------------------------------------

def _weekly_count(data: Dict[str, Any]) -> int:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    total = 0
    for entry in data.get("history", []):
        entry_date = date.fromisoformat(entry["date"])
        if entry_date >= week_start:
            total += entry["pomodoros"]
    return total


BADGES: List[Dict[str, Any]] = [
    {
        "id": "first_steps",
        "name": "🌱 ファーストステップ",
        "description": "最初のポモドーロを完了",
        "condition": lambda d: d.get("total_pomodoros", 0) >= 1,
    },
    {
        "id": "streak_3",
        "name": "🔥 3日連続",
        "description": "3日連続でポモドーロを実施",
        "condition": lambda d: d.get("streak", {}).get("current", 0) >= 3,
    },
    {
        "id": "streak_7",
        "name": "🔥🔥 1週間連続",
        "description": "7日連続でポモドーロを実施",
        "condition": lambda d: d.get("streak", {}).get("current", 0) >= 7,
    },
    {
        "id": "weekly_10",
        "name": "🏆 週間チャンピオン",
        "description": "同一週に10回以上ポモドーロを達成",
        "condition": lambda d: _weekly_count(d) >= 10,
    },
    {
        "id": "total_10",
        "name": "⭐ 10回達成",
        "description": "累計10回のポモドーロを完了",
        "condition": lambda d: d.get("total_pomodoros", 0) >= 10,
    },
    {
        "id": "total_50",
        "name": "💎 50回達成",
        "description": "累計50回のポモドーロを完了",
        "condition": lambda d: d.get("total_pomodoros", 0) >= 50,
    },
    {
        "id": "total_100",
        "name": "🎖️ センチュリオン",
        "description": "累計100回のポモドーロを完了",
        "condition": lambda d: d.get("total_pomodoros", 0) >= 100,
    },
    {
        "id": "level_5",
        "name": "🌟 レベル5",
        "description": "レベル5に到達",
        "condition": lambda d: d.get("level", 1) >= 5,
    },
    {
        "id": "level_10",
        "name": "👑 レベル10",
        "description": "レベル10に到達",
        "condition": lambda d: d.get("level", 1) >= 10,
    },
]


# ---------------------------------------------------------------------------
# XP / Level helpers
# ---------------------------------------------------------------------------

def xp_for_level(level: int) -> int:
    """Return XP required to advance *from* the given level to the next."""
    return level * _XP_BASE


def add_xp(data: Dict[str, Any], xp: int = XP_PER_POMODORO) -> Tuple[bool, int]:
    """Add *xp* to *data* and handle level-ups.

    Returns:
        (leveled_up, new_level) where *leveled_up* is True if at least one
        level-up occurred.
    """
    data["xp"] = data.get("xp", 0) + xp
    leveled_up = False
    while data["xp"] >= xp_for_level(data.get("level", 1)):
        data["xp"] -= xp_for_level(data["level"])
        data["level"] = data.get("level", 1) + 1
        leveled_up = True
    return leveled_up, data["level"]


def xp_progress(data: Dict[str, Any]) -> Tuple[int, int]:
    """Return (current_xp, xp_needed_for_next_level)."""
    return data.get("xp", 0), xp_for_level(data.get("level", 1))


# ---------------------------------------------------------------------------
# Streak helpers
# ---------------------------------------------------------------------------

def update_streak(data: Dict[str, Any]) -> bool:
    """Update the daily streak in *data*.

    Returns True if the streak counter was incremented (first call today),
    False if today was already recorded.
    """
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    streak = data.setdefault("streak", {"current": 0, "longest": 0, "last_date": None})
    last_date = streak.get("last_date")

    if last_date == today:
        return False  # Already counted today

    if last_date == yesterday:
        streak["current"] = streak.get("current", 0) + 1
    else:
        streak["current"] = 1  # Streak broken (or first day)

    streak["last_date"] = today

    if streak["current"] > streak.get("longest", 0):
        streak["longest"] = streak["current"]

    return True


# ---------------------------------------------------------------------------
# Badge helpers
# ---------------------------------------------------------------------------

def check_badges(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for newly earned badges and add them to *data*.

    Returns a list of newly earned badge dicts (empty list if none).
    """
    earned: set = set(data.get("badges", []))
    new_badges: List[Dict[str, Any]] = []
    for badge in BADGES:
        if badge["id"] not in earned and badge["condition"](data):
            earned.add(badge["id"])
            new_badges.append(badge)
    data["badges"] = list(earned)
    return new_badges


def get_earned_badges(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the list of earned badge dicts in definition order."""
    earned_ids: set = set(data.get("badges", []))
    return [b for b in BADGES if b["id"] in earned_ids]
