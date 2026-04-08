"""
pomodoro_stats.py - Statistics calculation and matplotlib graph rendering.

Named `pomodoro_stats` to avoid shadowing Python's built-in `statistics` module.
"""

from datetime import date, timedelta
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Pure-calculation helpers (no matplotlib dependency)
# ---------------------------------------------------------------------------

def get_daily_stats(data: Dict[str, Any], days: int = 7) -> Dict[str, Dict]:
    """Return a dict mapping date labels (MM/DD) to pomodoro/focus_minute counts.

    Keys are ordered from oldest to newest over the last *days* days.
    """
    today = date.today()
    stats: Dict[str, Dict] = {}
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        stats[d.strftime("%m/%d")] = {"pomodoros": 0, "focus_minutes": 0}

    for entry in data.get("history", []):
        entry_date = date.fromisoformat(entry["date"])
        delta = (today - entry_date).days
        if 0 <= delta < days:
            label = entry_date.strftime("%m/%d")
            if label in stats:
                stats[label]["pomodoros"] += entry["pomodoros"]
                stats[label]["focus_minutes"] += entry["focus_minutes"]
    return stats


def get_weekly_stats(data: Dict[str, Any], weeks: int = 4) -> Dict[str, Dict]:
    """Return a dict mapping week labels (MM/DD〜MM/DD) to pomodoro/focus counts."""
    today = date.today()
    stats: Dict[str, Dict] = {}
    for i in range(weeks - 1, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7 * i)
        week_end = week_start + timedelta(days=6)
        label = f"{week_start.strftime('%m/%d')}〜{week_end.strftime('%m/%d')}"
        stats[label] = {"pomodoros": 0, "focus_minutes": 0, "_start": week_start, "_end": week_end}

    for entry in data.get("history", []):
        entry_date = date.fromisoformat(entry["date"])
        for label, bucket in stats.items():
            if bucket["_start"] <= entry_date <= bucket["_end"]:
                bucket["pomodoros"] += entry["pomodoros"]
                bucket["focus_minutes"] += entry["focus_minutes"]
                break

    # Remove internal helper keys before returning
    for bucket in stats.values():
        bucket.pop("_start", None)
        bucket.pop("_end", None)
    return stats


def get_monthly_stats(data: Dict[str, Any], months: int = 6) -> Dict[str, Dict]:
    """Return a dict mapping month labels (YYYY/MM) to pomodoro/focus counts."""
    today = date.today()
    stats: Dict[str, Dict] = {}
    for i in range(months - 1, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        label = f"{year}/{month:02d}"
        stats[label] = {"pomodoros": 0, "focus_minutes": 0}

    for entry in data.get("history", []):
        entry_date = date.fromisoformat(entry["date"])
        label = f"{entry_date.year}/{entry_date.month:02d}"
        if label in stats:
            stats[label]["pomodoros"] += entry["pomodoros"]
            stats[label]["focus_minutes"] += entry["focus_minutes"]
    return stats


# ---------------------------------------------------------------------------
# Graph rendering (requires matplotlib)
# ---------------------------------------------------------------------------

def _configure_japanese_font() -> None:
    """Attempt to configure matplotlib to use a font that supports Japanese glyphs."""
    try:
        import matplotlib.font_manager as fm
        import matplotlib as mpl

        # Preferred fonts in order (common on Linux, macOS, Windows)
        candidates = [
            "Noto Sans CJK JP",
            "IPAexGothic",
            "IPAPGothic",
            "Meiryo",
            "MS Gothic",
            "Hiragino Sans",
            "Yu Gothic",
        ]
        available = {f.name for f in fm.fontManager.ttflist}
        for font in candidates:
            if font in available:
                mpl.rcParams["font.family"] = font
                return
        # No Japanese font found – charts will render with placeholder boxes for CJK chars
    except Exception:
        pass


def show_statistics_window(data: Dict[str, Any]) -> None:
    """Display a matplotlib window with daily and weekly bar charts."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        # Use a non-interactive backend if running without a display
        matplotlib.use("TkAgg")
    except ImportError:
        print(
            "統計グラフの表示には matplotlib が必要です。\n"
            "  pip install matplotlib\n"
            "でインストールしてください。"
        )
        return

    _configure_japanese_font()

    daily = get_daily_stats(data, days=7)
    weekly = get_weekly_stats(data, weeks=4)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("#2c3e50")
    fig.suptitle("ポモドーロ統計", fontsize=16, fontweight="bold", color="white")

    _draw_bar_chart(
        axes[0],
        labels=list(daily.keys()),
        values=[daily[k]["pomodoros"] for k in daily],
        title="過去7日間のポモドーロ数",
        xlabel="日付",
        bar_color="#e74c3c",
    )

    _draw_bar_chart(
        axes[1],
        labels=list(weekly.keys()),
        values=[weekly[k]["pomodoros"] for k in weekly],
        title="過去4週間のポモドーロ数",
        xlabel="週",
        bar_color="#3498db",
    )

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    plt.show()


def _draw_bar_chart(ax, labels, values, title, xlabel, bar_color):
    ax.set_facecolor("#34495e")
    bars = ax.bar(labels, values, color=bar_color, alpha=0.85, zorder=3)
    ax.set_title(title, color="white", fontsize=12)
    ax.set_xlabel(xlabel, color="#bdc3c7")
    ax.set_ylabel("ポモドーロ数", color="#bdc3c7")
    ax.set_ylim(0, max(list(values) + [1]) + 1)
    ax.tick_params(colors="#bdc3c7", axis="both")
    ax.spines[:].set_color("#4a5f72")
    ax.yaxis.grid(True, color="#4a5f72", linestyle="--", zorder=0)
    for bar, val in zip(bars, values):
        if val > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(val),
                ha="center",
                va="bottom",
                fontsize=9,
                color="white",
            )
    for tick in ax.get_xticklabels():
        tick.set_rotation(30)
        tick.set_ha("right")
