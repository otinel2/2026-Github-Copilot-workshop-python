"""Tests for gamification.py (XP/level, streak, badges)."""

import sys
import os
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gamification import (
    BADGES,
    XP_PER_POMODORO,
    add_xp,
    check_badges,
    get_earned_badges,
    update_streak,
    xp_for_level,
    xp_progress,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_data(**kwargs):
    data = {
        "total_pomodoros": 0,
        "xp": 0,
        "level": 1,
        "streak": {"current": 0, "longest": 0, "last_date": None},
        "badges": [],
        "history": [],
    }
    data.update(kwargs)
    return data


# ---------------------------------------------------------------------------
# XP / Level
# ---------------------------------------------------------------------------

class TestXpForLevel:
    def test_level_1_needs_100(self):
        assert xp_for_level(1) == 100

    def test_level_2_needs_200(self):
        assert xp_for_level(2) == 200

    def test_proportional(self):
        assert xp_for_level(5) == 500


class TestAddXp:
    def test_no_level_up(self):
        data = _make_data()
        leveled_up, level = add_xp(data, 10)
        assert not leveled_up
        assert level == 1
        assert data["xp"] == 10

    def test_exact_level_up(self):
        data = _make_data(xp=90)
        leveled_up, level = add_xp(data, 10)  # 90 + 10 = 100 => level up
        assert leveled_up
        assert level == 2
        assert data["xp"] == 0

    def test_level_up_with_remainder(self):
        data = _make_data(xp=95)
        leveled_up, level = add_xp(data, 10)  # 105 >= 100 => level 2, leftover 5
        assert leveled_up
        assert level == 2
        assert data["xp"] == 5

    def test_multiple_level_ups(self):
        # Level 1 needs 100, level 2 needs 200 => total 300 for level 3
        data = _make_data(xp=0, level=1)
        leveled_up, level = add_xp(data, 350)
        assert leveled_up
        assert level == 3

    def test_xp_per_pomodoro_constant(self):
        assert XP_PER_POMODORO == 10


class TestXpProgress:
    def test_fresh(self):
        data = _make_data(xp=0, level=1)
        cur, needed = xp_progress(data)
        assert cur == 0
        assert needed == 100

    def test_partial(self):
        data = _make_data(xp=30, level=2)
        cur, needed = xp_progress(data)
        assert cur == 30
        assert needed == 200


# ---------------------------------------------------------------------------
# Streak
# ---------------------------------------------------------------------------

class TestUpdateStreak:
    def test_first_day_starts_streak(self):
        data = _make_data()
        result = update_streak(data)
        assert result is True
        assert data["streak"]["current"] == 1
        assert data["streak"]["longest"] == 1
        assert data["streak"]["last_date"] == date.today().isoformat()

    def test_consecutive_day_increments(self):
        data = _make_data()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        data["streak"]["last_date"] = yesterday
        data["streak"]["current"] = 3
        data["streak"]["longest"] = 3
        result = update_streak(data)
        assert result is True
        assert data["streak"]["current"] == 4
        assert data["streak"]["longest"] == 4

    def test_broken_streak_resets_to_one(self):
        data = _make_data()
        two_days_ago = (date.today() - timedelta(days=2)).isoformat()
        data["streak"]["last_date"] = two_days_ago
        data["streak"]["current"] = 5
        data["streak"]["longest"] = 5
        update_streak(data)
        assert data["streak"]["current"] == 1
        # Longest should be preserved
        assert data["streak"]["longest"] == 5

    def test_same_day_returns_false_and_no_change(self):
        data = _make_data()
        today = date.today().isoformat()
        data["streak"]["last_date"] = today
        data["streak"]["current"] = 3
        result = update_streak(data)
        assert result is False
        assert data["streak"]["current"] == 3

    def test_longest_updated(self):
        data = _make_data()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        data["streak"]["last_date"] = yesterday
        data["streak"]["current"] = 9
        data["streak"]["longest"] = 9
        update_streak(data)
        assert data["streak"]["longest"] == 10


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------

class TestCheckBadges:
    def test_first_steps_earned_at_one_pomodoro(self):
        data = _make_data(total_pomodoros=1)
        new_badges = check_badges(data)
        ids = [b["id"] for b in new_badges]
        assert "first_steps" in ids

    def test_no_badge_before_threshold(self):
        data = _make_data(total_pomodoros=0)
        new_badges = check_badges(data)
        ids = [b["id"] for b in new_badges]
        assert "first_steps" not in ids

    def test_streak_3_badge(self):
        data = _make_data()
        data["streak"]["current"] = 3
        new_badges = check_badges(data)
        ids = [b["id"] for b in new_badges]
        assert "streak_3" in ids

    def test_streak_7_badge(self):
        data = _make_data()
        data["streak"]["current"] = 7
        new_badges = check_badges(data)
        ids = [b["id"] for b in new_badges]
        assert "streak_7" in ids
        assert "streak_3" in ids  # lower threshold also earned

    def test_total_10_badge(self):
        data = _make_data(total_pomodoros=10)
        ids = [b["id"] for b in check_badges(data)]
        assert "total_10" in ids

    def test_total_50_badge(self):
        data = _make_data(total_pomodoros=50)
        ids = [b["id"] for b in check_badges(data)]
        assert "total_50" in ids

    def test_total_100_badge(self):
        data = _make_data(total_pomodoros=100)
        ids = [b["id"] for b in check_badges(data)]
        assert "total_100" in ids

    def test_level_5_badge(self):
        data = _make_data(level=5)
        ids = [b["id"] for b in check_badges(data)]
        assert "level_5" in ids

    def test_level_10_badge(self):
        data = _make_data(level=10)
        ids = [b["id"] for b in check_badges(data)]
        assert "level_10" in ids
        assert "level_5" in ids

    def test_no_duplicate_badges(self):
        data = _make_data(total_pomodoros=1, badges=["first_steps"])
        new_badges = check_badges(data)
        ids = [b["id"] for b in new_badges]
        assert "first_steps" not in ids

    def test_badges_stored_in_data(self):
        data = _make_data(total_pomodoros=1)
        check_badges(data)
        assert "first_steps" in data["badges"]

    def test_weekly_10_badge(self):
        today = date.today().isoformat()
        data = _make_data()
        data["history"] = [{"date": today, "pomodoros": 10, "focus_minutes": 250}]
        ids = [b["id"] for b in check_badges(data)]
        assert "weekly_10" in ids


class TestGetEarnedBadges:
    def test_returns_earned_in_definition_order(self):
        data = _make_data(badges=["total_10", "first_steps"])
        earned = get_earned_badges(data)
        earned_ids = [b["id"] for b in earned]
        assert "first_steps" in earned_ids
        assert "total_10" in earned_ids
        # first_steps comes before total_10 in BADGES definition
        assert earned_ids.index("first_steps") < earned_ids.index("total_10")

    def test_empty_if_no_badges(self):
        data = _make_data()
        assert get_earned_badges(data) == []

    def test_badge_has_required_fields(self):
        data = _make_data(badges=["first_steps"])
        earned = get_earned_badges(data)
        assert len(earned) == 1
        badge = earned[0]
        assert "id" in badge
        assert "name" in badge
        assert "description" in badge
