"""Tests for pomodoro_stats.py (statistics calculations, no matplotlib required)."""

import sys
import os
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pomodoro_stats import (
    get_achievement_rate,
    get_avg_focus_minutes,
    get_daily_stats,
    get_monthly_stats,
    get_weekly_stats,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_data(history=None):
    return {
        "total_pomodoros": 0,
        "xp": 0,
        "level": 1,
        "streak": {"current": 0, "longest": 0, "last_date": None},
        "badges": [],
        "history": history or [],
    }


def _days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


# ---------------------------------------------------------------------------
# Daily stats
# ---------------------------------------------------------------------------

class TestGetDailyStats:
    def test_returns_seven_keys_by_default(self):
        data = _make_data()
        stats = get_daily_stats(data)
        assert len(stats) == 7

    def test_all_zero_with_no_history(self):
        data = _make_data()
        stats = get_daily_stats(data)
        assert all(v["pomodoros"] == 0 for v in stats.values())

    def test_today_entry_counted(self):
        today = date.today().isoformat()
        data = _make_data(history=[{"date": today, "pomodoros": 3, "focus_minutes": 75}])
        stats = get_daily_stats(data)
        today_label = date.today().strftime("%m/%d")
        assert stats[today_label]["pomodoros"] == 3
        assert stats[today_label]["focus_minutes"] == 75

    def test_old_entry_not_counted(self):
        old = _days_ago(10)
        data = _make_data(history=[{"date": old, "pomodoros": 5, "focus_minutes": 125}])
        stats = get_daily_stats(data, days=7)
        assert all(v["pomodoros"] == 0 for v in stats.values())

    def test_custom_days_count(self):
        data = _make_data()
        stats = get_daily_stats(data, days=14)
        assert len(stats) == 14

    def test_multiple_entries_summed(self):
        today = date.today().isoformat()
        yesterday = _days_ago(1)
        data = _make_data(
            history=[
                {"date": today, "pomodoros": 2, "focus_minutes": 50},
                {"date": yesterday, "pomodoros": 3, "focus_minutes": 75},
            ]
        )
        stats = get_daily_stats(data)
        today_label = date.today().strftime("%m/%d")
        yest_label = (date.today() - timedelta(days=1)).strftime("%m/%d")
        assert stats[today_label]["pomodoros"] == 2
        assert stats[yest_label]["pomodoros"] == 3


# ---------------------------------------------------------------------------
# Weekly stats
# ---------------------------------------------------------------------------

class TestGetWeeklyStats:
    def test_returns_four_keys_by_default(self):
        data = _make_data()
        stats = get_weekly_stats(data)
        assert len(stats) == 4

    def test_all_zero_with_no_history(self):
        data = _make_data()
        stats = get_weekly_stats(data)
        assert all(v["pomodoros"] == 0 for v in stats.values())

    def test_current_week_entry_counted(self):
        today = date.today().isoformat()
        data = _make_data(history=[{"date": today, "pomodoros": 5, "focus_minutes": 125}])
        stats = get_weekly_stats(data)
        # The last key corresponds to the current week
        last_week = list(stats.values())[-1]
        assert last_week["pomodoros"] == 5

    def test_no_internal_start_end_keys(self):
        data = _make_data()
        stats = get_weekly_stats(data)
        for bucket in stats.values():
            assert "_start" not in bucket
            assert "_end" not in bucket


# ---------------------------------------------------------------------------
# Monthly stats
# ---------------------------------------------------------------------------

class TestGetMonthlyStats:
    def test_returns_six_keys_by_default(self):
        data = _make_data()
        stats = get_monthly_stats(data)
        assert len(stats) == 6

    def test_all_zero_with_no_history(self):
        data = _make_data()
        stats = get_monthly_stats(data)
        assert all(v["pomodoros"] == 0 for v in stats.values())

    def test_current_month_entry_counted(self):
        today = date.today().isoformat()
        data = _make_data(history=[{"date": today, "pomodoros": 4, "focus_minutes": 100}])
        stats = get_monthly_stats(data)
        this_month = f"{date.today().year}/{date.today().month:02d}"
        assert stats[this_month]["pomodoros"] == 4


# ---------------------------------------------------------------------------
# Achievement rate
# ---------------------------------------------------------------------------

class TestGetAchievementRate:
    def test_zero_with_no_history(self):
        data = _make_data()
        rate = get_achievement_rate(data, days=7)
        assert rate == 0.0

    def test_full_rate_every_day_active(self):
        history = [
            {"date": _days_ago(i), "pomodoros": 1, "focus_minutes": 25}
            for i in range(7)
        ]
        data = _make_data(history=history)
        rate = get_achievement_rate(data, days=7)
        assert rate == 1.0

    def test_partial_rate(self):
        # Only today has pomodoros out of a 7-day window
        history = [{"date": _days_ago(0), "pomodoros": 2, "focus_minutes": 50}]
        data = _make_data(history=history)
        rate = get_achievement_rate(data, days=7)
        assert abs(rate - 1 / 7) < 1e-9

    def test_returns_zero_for_zero_days(self):
        data = _make_data()
        assert get_achievement_rate(data, days=0) == 0.0

    def test_old_history_not_counted(self):
        old = _days_ago(10)
        data = _make_data(history=[{"date": old, "pomodoros": 5, "focus_minutes": 125}])
        rate = get_achievement_rate(data, days=7)
        assert rate == 0.0


# ---------------------------------------------------------------------------
# Average focus minutes
# ---------------------------------------------------------------------------

class TestGetAvgFocusMinutes:
    def test_zero_with_no_history(self):
        data = _make_data()
        avg = get_avg_focus_minutes(data, days=7)
        assert avg == 0.0

    def test_single_active_day(self):
        history = [{"date": _days_ago(0), "pomodoros": 2, "focus_minutes": 50}]
        data = _make_data(history=history)
        avg = get_avg_focus_minutes(data, days=7)
        assert avg == 50.0

    def test_average_of_two_active_days(self):
        history = [
            {"date": _days_ago(0), "pomodoros": 2, "focus_minutes": 50},
            {"date": _days_ago(1), "pomodoros": 1, "focus_minutes": 25},
        ]
        data = _make_data(history=history)
        avg = get_avg_focus_minutes(data, days=7)
        assert avg == 37.5  # (50 + 25) / 2

    def test_old_history_excluded(self):
        old = _days_ago(10)
        data = _make_data(history=[{"date": old, "pomodoros": 4, "focus_minutes": 100}])
        avg = get_avg_focus_minutes(data, days=7)
        assert avg == 0.0

    def test_day_with_zero_pomodoros_excluded_from_avg(self):
        # History entry with 0 pomodoros should not count towards the average
        history = [
            {"date": _days_ago(0), "pomodoros": 0, "focus_minutes": 0},
            {"date": _days_ago(1), "pomodoros": 2, "focus_minutes": 50},
        ]
        data = _make_data(history=history)
        avg = get_avg_focus_minutes(data, days=7)
        assert avg == 50.0
