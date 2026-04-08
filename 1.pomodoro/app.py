#!/usr/bin/env python3
# Pomodoro Timer App with Gamification (XP・バッジ・統計・連続記録)

import tkinter as tk
from tkinter import messagebox

from data_store import add_pomodoro_session, load_data, save_data
from gamification import (
    XP_PER_POMODORO,
    add_xp,
    check_badges,
    get_earned_badges,
    update_streak,
    xp_progress,
)
from pomodoro_stats import show_statistics_window

# ---------------------------------------------------------------------------
# Timer constants
# ---------------------------------------------------------------------------
WORK_MINUTES = 25
SHORT_BREAK_MINUTES = 5
LONG_BREAK_MINUTES = 15
POMODOROS_UNTIL_LONG_BREAK = 4

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
BG_COLOR = "#2c3e50"
WORK_COLOR = "#e74c3c"
SHORT_BREAK_COLOR = "#2ecc71"
LONG_BREAK_COLOR = "#3498db"
TEXT_COLOR = "#ecf0f1"
MUTED_COLOR = "#bdc3c7"
CARD_COLOR = "#34495e"
ACCENT_COLOR = "#f39c12"
XP_BAR_COLOR = "#9b59b6"


# ---------------------------------------------------------------------------
# Level display names
# ---------------------------------------------------------------------------
_LEVEL_NAMES = {
    1: "フォーカス見習い",
    2: "フォーカス初級",
    3: "フォーカス中級",
    4: "フォーカス上級",
    5: "フォーカスマスター",
    6: "フォーカス達人",
    7: "フォーカス伝説",
    8: "フォーカス神話",
    9: "フォーカス覇者",
    10: "フォーカス王者",
}


def _level_name(level: int) -> str:
    return _LEVEL_NAMES.get(level, f"フォーカス超越者 Lv.{level}")


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

class PomodoroApp:
    """Pomodoro timer with XP, level, streak, badges, and statistics."""

    _MODE_MINUTES = {
        "work": WORK_MINUTES,
        "short_break": SHORT_BREAK_MINUTES,
        "long_break": LONG_BREAK_MINUTES,
    }
    _MODE_NAMES = {
        "work": "作業時間",
        "short_break": "短い休憩",
        "long_break": "長い休憩",
    }
    _MODE_COLORS = {
        "work": WORK_COLOR,
        "short_break": SHORT_BREAK_COLOR,
        "long_break": LONG_BREAK_COLOR,
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🍅 ポモドーロタイマー")
        self.root.geometry("520x720")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.data = load_data()

        # Timer state
        self.current_mode = "work"
        self.current_seconds = WORK_MINUTES * 60
        self._total_seconds = WORK_MINUTES * 60
        self._timer_running = False
        self._after_id: str | None = None
        self._session_pomodoros = 0

        self._build_ui()
        self._refresh_display()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Title
        tk.Label(
            self.root,
            text="🍅 ポモドーロタイマー",
            font=("Helvetica", 20, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(pady=(14, 4))

        # Mode selector buttons
        mode_frame = tk.Frame(self.root, bg=BG_COLOR)
        mode_frame.pack(pady=4)
        self._mode_btns: dict[str, tk.Button] = {}
        for label, mode in [("作業", "work"), ("短い休憩", "short_break"), ("長い休憩", "long_break")]:
            btn = tk.Button(
                mode_frame,
                text=label,
                font=("Helvetica", 10),
                bg=CARD_COLOR,
                fg=TEXT_COLOR,
                activebackground="#4a5f72",
                activeforeground=TEXT_COLOR,
                relief="flat",
                padx=12,
                pady=4,
                command=lambda m=mode: self._switch_mode(m),
            )
            btn.pack(side="left", padx=4)
            self._mode_btns[mode] = btn

        # ---- Timer canvas ----
        canvas_frame = tk.Frame(self.root, bg=BG_COLOR)
        canvas_frame.pack(pady=12)

        self._canvas = tk.Canvas(
            canvas_frame, width=220, height=220, bg=BG_COLOR, highlightthickness=0
        )
        self._canvas.pack()

        self._arc = self._canvas.create_arc(
            10, 10, 210, 210,
            start=90,
            extent=360,
            outline=WORK_COLOR,
            width=10,
            style="arc",
        )
        self._timer_label = tk.Label(
            canvas_frame,
            text=self._seconds_to_str(self.current_seconds),
            font=("Helvetica", 50, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        self._timer_label.place(in_=self._canvas, relx=0.5, rely=0.47, anchor="center")

        self._mode_name_label = tk.Label(
            canvas_frame,
            text=self._MODE_NAMES["work"],
            font=("Helvetica", 13),
            bg=BG_COLOR,
            fg=MUTED_COLOR,
        )
        self._mode_name_label.place(in_=self._canvas, relx=0.5, rely=0.76, anchor="center")

        # ---- Control buttons ----
        ctrl_frame = tk.Frame(self.root, bg=BG_COLOR)
        ctrl_frame.pack(pady=4)

        self._start_btn = tk.Button(
            ctrl_frame,
            text="▶ スタート",
            font=("Helvetica", 13, "bold"),
            bg=WORK_COLOR,
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief="flat",
            padx=22,
            pady=8,
            command=self._toggle_timer,
        )
        self._start_btn.pack(side="left", padx=6)

        tk.Button(
            ctrl_frame,
            text="↺ リセット",
            font=("Helvetica", 13),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            activebackground="#4a5f72",
            activeforeground=TEXT_COLOR,
            relief="flat",
            padx=22,
            pady=8,
            command=self._reset_timer,
        ).pack(side="left", padx=6)

        # ---- Divider ----
        tk.Frame(self.root, height=1, bg="#4a5f72").pack(fill="x", padx=20, pady=10)

        # ---- Streak + Today row ----
        stats_frame = tk.Frame(self.root, bg=BG_COLOR)
        stats_frame.pack(fill="x", padx=24, pady=2)

        # Streak card
        streak_card = tk.Frame(stats_frame, bg=CARD_COLOR, padx=10, pady=8)
        streak_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(streak_card, text="🔥 ストリーク", font=("Helvetica", 10), bg=CARD_COLOR, fg=MUTED_COLOR).pack()
        self._streak_label = tk.Label(
            streak_card, text="0日", font=("Helvetica", 22, "bold"), bg=CARD_COLOR, fg=ACCENT_COLOR
        )
        self._streak_label.pack()

        # Today's count card
        today_card = tk.Frame(stats_frame, bg=CARD_COLOR, padx=10, pady=8)
        today_card.pack(side="left", fill="both", expand=True, padx=(5, 0))
        tk.Label(today_card, text="🍅 今日の完了数", font=("Helvetica", 10), bg=CARD_COLOR, fg=MUTED_COLOR).pack()
        self._today_label = tk.Label(
            today_card, text="0回", font=("Helvetica", 22, "bold"), bg=CARD_COLOR, fg=WORK_COLOR
        )
        self._today_label.pack()

        # ---- Level + XP bar ----
        level_row = tk.Frame(self.root, bg=BG_COLOR)
        level_row.pack(fill="x", padx=24, pady=(10, 2))

        self._level_label = tk.Label(
            level_row,
            text="Lv.1 フォーカス見習い",
            font=("Helvetica", 11, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        self._level_label.pack(side="left")

        self._xp_text_label = tk.Label(
            level_row, text="0 / 100 XP", font=("Helvetica", 10), bg=BG_COLOR, fg=MUTED_COLOR
        )
        self._xp_text_label.pack(side="right")

        self._xp_canvas = tk.Canvas(
            self.root, height=12, bg=CARD_COLOR, highlightthickness=0
        )
        self._xp_canvas.pack(fill="x", padx=24, pady=(0, 4))
        self._xp_fill = self._xp_canvas.create_rectangle(0, 0, 0, 12, fill=XP_BAR_COLOR, outline="")

        # Total counter
        self._total_label = tk.Label(
            self.root,
            text="累計ポモドーロ: 0回",
            font=("Helvetica", 10),
            bg=BG_COLOR,
            fg=MUTED_COLOR,
        )
        self._total_label.pack(pady=2)

        # ---- Divider ----
        tk.Frame(self.root, height=1, bg="#4a5f72").pack(fill="x", padx=20, pady=6)

        # ---- Badges header ----
        badge_header = tk.Frame(self.root, bg=BG_COLOR)
        badge_header.pack(fill="x", padx=24)

        tk.Label(
            badge_header, text="🏅 バッジ", font=("Helvetica", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR
        ).pack(side="left")

        tk.Button(
            badge_header,
            text="📊 統計を見る",
            font=("Helvetica", 10),
            bg="#2980b9",
            fg="white",
            activebackground="#1a6799",
            activeforeground="white",
            relief="flat",
            padx=8,
            pady=3,
            command=self._show_stats,
        ).pack(side="right")

        # ---- Badge display area ----
        self._badges_frame = tk.Frame(self.root, bg=BG_COLOR)
        self._badges_frame.pack(fill="x", padx=24, pady=6)

    # ------------------------------------------------------------------
    # Display refresh
    # ------------------------------------------------------------------

    def _refresh_display(self) -> None:
        from datetime import date as _date

        # Streak
        streak = self.data.get("streak", {}).get("current", 0)
        self._streak_label.config(text=f"{streak}日")

        # Today count
        today_str = _date.today().isoformat()
        today_count = 0
        for entry in self.data.get("history", []):
            if entry["date"] == today_str:
                today_count = entry["pomodoros"]
                break
        self._today_label.config(text=f"{today_count}回")

        # Level / XP
        level = self.data.get("level", 1)
        xp, xp_needed = xp_progress(self.data)
        self._level_label.config(text=f"Lv.{level} {_level_name(level)}")
        self._xp_text_label.config(text=f"{xp} / {xp_needed} XP")

        # XP bar fill
        self._xp_canvas.update_idletasks()
        bar_w = self._xp_canvas.winfo_width()
        if bar_w > 1 and xp_needed > 0:
            fill_w = int(bar_w * xp / xp_needed)
            self._xp_canvas.coords(self._xp_fill, 0, 0, fill_w, 12)

        # Total
        self._total_label.config(text=f"累計ポモドーロ: {self.data.get('total_pomodoros', 0)}回")

        # Timer arc colour
        color = self._MODE_COLORS[self.current_mode]
        self._canvas.itemconfig(self._arc, outline=color)
        self._mode_name_label.config(text=self._MODE_NAMES[self.current_mode])

        # Badges
        self._refresh_badges()

    def _refresh_badges(self) -> None:
        for widget in self._badges_frame.winfo_children():
            widget.destroy()

        earned = get_earned_badges(self.data)
        if not earned:
            tk.Label(
                self._badges_frame,
                text="まだバッジがありません。ポモドーロを始めましょう！",
                font=("Helvetica", 9),
                bg=BG_COLOR,
                fg="#7f8c8d",
                wraplength=460,
            ).pack(anchor="w")
            return

        row = tk.Frame(self._badges_frame, bg=BG_COLOR)
        row.pack(fill="x")
        for i, badge in enumerate(earned):
            if i > 0 and i % 3 == 0:
                row = tk.Frame(self._badges_frame, bg=BG_COLOR)
                row.pack(fill="x", pady=2)
            lbl = tk.Label(
                row,
                text=badge["name"],
                font=("Helvetica", 9),
                bg="#2d4a3e",
                fg="#2ecc71",
                relief="flat",
                padx=6,
                pady=3,
                cursor="hand2",
            )
            lbl.pack(side="left", padx=3)
            lbl.bind("<Enter>", lambda e, b=badge: self._show_tooltip(e, b["description"]))

    def _show_tooltip(self, event: tk.Event, text: str) -> None:
        tip = tk.Toplevel(self.root)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{event.x_root + 12}+{event.y_root + 12}")
        tk.Label(
            tip,
            text=text,
            bg="#2c3e50",
            fg="white",
            font=("Helvetica", 10),
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=4,
        ).pack()
        tip.after(2000, tip.destroy)

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------

    def _switch_mode(self, mode: str) -> None:
        if self._timer_running:
            return
        self.current_mode = mode
        self.current_seconds = self._MODE_MINUTES[mode] * 60
        self._total_seconds = self.current_seconds
        self._timer_label.config(text=self._seconds_to_str(self.current_seconds))
        self._canvas.itemconfig(self._arc, extent=360)
        self._refresh_display()

    # ------------------------------------------------------------------
    # Timer control
    # ------------------------------------------------------------------

    def _toggle_timer(self) -> None:
        if self._timer_running:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self) -> None:
        if self.current_seconds == 0:
            return
        self._timer_running = True
        self._total_seconds = self._total_seconds or self.current_seconds
        self._start_btn.config(text="⏸ 一時停止", bg="#e67e22")
        self._tick()

    def _pause_timer(self) -> None:
        self._timer_running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self._start_btn.config(text="▶ 再開", bg=WORK_COLOR)

    def _reset_timer(self) -> None:
        self._timer_running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.current_seconds = self._MODE_MINUTES[self.current_mode] * 60
        self._total_seconds = self.current_seconds
        self._start_btn.config(text="▶ スタート", bg=WORK_COLOR)
        self._timer_label.config(text=self._seconds_to_str(self.current_seconds))
        self._canvas.itemconfig(self._arc, extent=360)

    def _tick(self) -> None:
        if not self._timer_running:
            return
        if self.current_seconds > 0:
            self.current_seconds -= 1
            self._timer_label.config(text=self._seconds_to_str(self.current_seconds))
            # Arc: show remaining fraction (full circle = 360, empty = 0)
            if self._total_seconds > 0:
                extent = 360 * self.current_seconds / self._total_seconds
                self._canvas.itemconfig(self._arc, extent=extent)
            self._after_id = self.root.after(1000, self._tick)
        else:
            self._on_timer_complete()

    # ------------------------------------------------------------------
    # Timer completion
    # ------------------------------------------------------------------

    def _on_timer_complete(self) -> None:
        self._timer_running = False
        self._after_id = None
        self._start_btn.config(text="▶ スタート", bg=WORK_COLOR)
        self._canvas.itemconfig(self._arc, extent=360)

        if self.current_mode == "work":
            self._session_pomodoros += 1

            # Update gamification data
            add_pomodoro_session(self.data, focus_minutes=WORK_MINUTES)
            leveled_up, new_level = add_xp(self.data)
            update_streak(self.data)
            new_badges = check_badges(self.data)
            save_data(self.data)
            self._refresh_display()

            # Build notification
            msg = f"🍅 ポモドーロ完了！\n+{XP_PER_POMODORO} XP 獲得！"
            if leveled_up:
                msg += f"\n🎉 レベルアップ！ Lv.{new_level} {_level_name(new_level)} になりました！"
            if new_badges:
                badge_names = "、".join(b["name"] for b in new_badges)
                msg += f"\n🏅 新バッジ獲得: {badge_names}"

            messagebox.showinfo("完了！", msg)

            # Determine next break
            if self._session_pomodoros % POMODOROS_UNTIL_LONG_BREAK == 0:
                self._switch_mode("long_break")
                messagebox.showinfo("長い休憩", f"長い休憩タイムです！（{LONG_BREAK_MINUTES}分）")
            else:
                self._switch_mode("short_break")
                messagebox.showinfo("短い休憩", f"短い休憩タイムです！（{SHORT_BREAK_MINUTES}分）")
        else:
            messagebox.showinfo("休憩終了", "休憩が終わりました。作業を再開しましょう！")
            self._switch_mode("work")

    # ------------------------------------------------------------------
    # Stats window
    # ------------------------------------------------------------------

    def _show_stats(self) -> None:
        show_statistics_window(self.data)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _seconds_to_str(seconds: int) -> str:
        return f"{seconds // 60:02d}:{seconds % 60:02d}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    root = tk.Tk()
    PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
