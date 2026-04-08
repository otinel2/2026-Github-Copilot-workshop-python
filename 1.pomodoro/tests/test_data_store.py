"""Tests for data_store.py."""

import sys
import os
import json
import tempfile
from datetime import date

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import data_store


@pytest.fixture()
def tmp_data_file(monkeypatch, tmp_path):
    """Redirect DATA_FILE to a temporary path for isolation."""
    tmp_file = str(tmp_path / "test_data.json")
    monkeypatch.setattr(data_store, "DATA_FILE", tmp_file)
    return tmp_file


class TestLoadData:
    def test_returns_defaults_when_no_file(self, tmp_data_file):
        data = data_store.load_data()
        assert data["total_pomodoros"] == 0
        assert data["level"] == 1
        assert data["xp"] == 0
        assert data["streak"]["current"] == 0
        assert data["badges"] == []
        assert data["history"] == []

    def test_loads_existing_file(self, tmp_data_file):
        saved = {"total_pomodoros": 5, "xp": 30, "level": 2,
                 "streak": {"current": 2, "longest": 3, "last_date": "2024-01-01"},
                 "badges": ["first_steps"], "history": []}
        with open(tmp_data_file, "w") as f:
            json.dump(saved, f)
        data = data_store.load_data()
        assert data["total_pomodoros"] == 5
        assert data["level"] == 2

    def test_back_fills_missing_keys(self, tmp_data_file):
        # File missing some keys
        with open(tmp_data_file, "w") as f:
            json.dump({"total_pomodoros": 1}, f)
        data = data_store.load_data()
        assert "xp" in data
        assert "badges" in data


class TestSaveData:
    def test_save_and_reload(self, tmp_data_file):
        data = data_store.load_data()
        data["total_pomodoros"] = 42
        data_store.save_data(data)
        reloaded = data_store.load_data()
        assert reloaded["total_pomodoros"] == 42

    def test_file_is_valid_json(self, tmp_data_file):
        data = data_store.load_data()
        data_store.save_data(data)
        with open(tmp_data_file, "r") as f:
            parsed = json.load(f)
        assert isinstance(parsed, dict)


class TestAddPomodoroSession:
    def test_increments_total(self, tmp_data_file):
        data = data_store.load_data()
        data_store.add_pomodoro_session(data)
        assert data["total_pomodoros"] == 1

    def test_adds_history_entry(self, tmp_data_file):
        data = data_store.load_data()
        data_store.add_pomodoro_session(data, focus_minutes=25)
        today = date.today().isoformat()
        assert any(e["date"] == today for e in data["history"])

    def test_accumulates_same_day(self, tmp_data_file):
        data = data_store.load_data()
        data_store.add_pomodoro_session(data, focus_minutes=25)
        data_store.add_pomodoro_session(data, focus_minutes=25)
        today = date.today().isoformat()
        entry = next(e for e in data["history"] if e["date"] == today)
        assert entry["pomodoros"] == 2
        assert entry["focus_minutes"] == 50

    def test_focus_minutes_default(self, tmp_data_file):
        data = data_store.load_data()
        data_store.add_pomodoro_session(data)
        today = date.today().isoformat()
        entry = next(e for e in data["history"] if e["date"] == today)
        assert entry["focus_minutes"] == 25
