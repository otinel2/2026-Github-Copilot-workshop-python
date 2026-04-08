"""Visual effects for Pomodoro timer: color interpolation, particles, ripples."""
from __future__ import annotations

import math
import random
import tkinter as tk


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def _lerp_channel(c1: int, c2: int, t: float) -> int:
    return max(0, min(255, int(c1 + (c2 - c1) * t)))


def lerp_color(hex1: str, hex2: str, t: float) -> str:
    """Linearly interpolate between two hex colors (#rrggbb)."""
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    r = _lerp_channel(r1, r2, t)
    g = _lerp_channel(g1, g2, t)
    b = _lerp_channel(b1, b2, t)
    return f"#{r:02x}{g:02x}{b:02x}"


def progress_arc_color(fraction: float) -> str:
    """Return arc color based on remaining time fraction (1.0=full, 0.0=empty).

    Transition: blue (#3498db) → yellow (#f39c12) → red (#e74c3c).
    """
    _BLUE = "#3498db"
    _YELLOW = "#f39c12"
    _RED = "#e74c3c"
    fraction = max(0.0, min(1.0, fraction))
    if fraction >= 0.5:
        t = (1.0 - fraction) * 2.0  # 0 at fraction=1.0, 1 at fraction=0.5
        return lerp_color(_BLUE, _YELLOW, t)
    else:
        t = (0.5 - fraction) * 2.0  # 0 at fraction=0.5, 1 at fraction=0.0
        return lerp_color(_YELLOW, _RED, t)


# ---------------------------------------------------------------------------
# Particle system
# ---------------------------------------------------------------------------

class ParticleSystem:
    """Floating particles rendered on a tkinter Canvas during focus time."""

    _COUNT = 14
    _INTERVAL_MS = 50

    def __init__(self, canvas: tk.Canvas, cx: int, cy: int, radius: int) -> None:
        self._canvas = canvas
        self._cx = cx
        self._cy = cy
        self._radius = radius
        self._particles: list[dict] = []
        self._item_ids: list[int] = []
        self._running = False
        self._after_id: str | None = None
        self._spawn_all()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._loop()

    def stop(self) -> None:
        self._running = False
        if self._after_id is not None:
            self._canvas.after_cancel(self._after_id)
            self._after_id = None
        self._clear_items()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _spawn_all(self) -> None:
        self._particles = [self._new_particle() for _ in range(self._COUNT)]

    def _new_particle(self) -> dict:
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(self._radius * 0.25, self._radius - 18)
        return {
            "x": self._cx + dist * math.cos(angle),
            "y": self._cy + dist * math.sin(angle),
            "vx": random.uniform(-0.35, 0.35),
            "vy": random.uniform(-0.7, -0.15),
            "size": random.uniform(2.0, 4.5),
            "life": random.uniform(0.4, 1.0),
        }

    def _clear_items(self) -> None:
        for item_id in self._item_ids:
            self._canvas.delete(item_id)
        self._item_ids.clear()

    def _loop(self) -> None:
        if not self._running:
            return
        self._clear_items()
        updated = []
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.012
            if p["life"] <= 0:
                p = self._new_particle()
            updated.append(p)
            shade = int(180 + 75 * p["life"])
            color = f"#{shade:02x}{shade:02x}{min(255, shade + 40):02x}"
            s = p["size"]
            x, y = p["x"], p["y"]
            item_id = self._canvas.create_oval(
                x - s, y - s, x + s, y + s,
                fill=color, outline="", tags="particle",
            )
            self._item_ids.append(item_id)
        self._particles = updated
        # Keep particles behind the arc and text
        self._canvas.tag_lower("particle")
        self._after_id = self._canvas.after(self._INTERVAL_MS, self._loop)


# ---------------------------------------------------------------------------
# Ripple effect
# ---------------------------------------------------------------------------

class RippleEffect:
    """Expanding ring ripple animation from a central point on a Canvas."""

    _INTERVAL_MS = 30

    def __init__(self, canvas: tk.Canvas, cx: int, cy: int) -> None:
        self._canvas = canvas
        self._cx = cx
        self._cy = cy
        self._ripples: list[dict] = []
        self._item_ids: list[int] = []
        self._running = False
        self._after_id: str | None = None

    def trigger(self) -> None:
        """Spawn a new ripple from the center."""
        self._ripples.append({"radius": 8.0, "alpha": 1.0})
        if not self._running:
            self._running = True
            self._loop()

    def _loop(self) -> None:
        for item_id in self._item_ids:
            self._canvas.delete(item_id)
        self._item_ids.clear()
        remaining = []
        for ripple in self._ripples:
            ripple["radius"] += 5.0
            ripple["alpha"] -= 0.04
            if ripple["alpha"] <= 0:
                continue
            remaining.append(ripple)
            shade = int(255 * ripple["alpha"])
            color = f"#{shade:02x}{shade:02x}{shade:02x}"
            r = ripple["radius"]
            item_id = self._canvas.create_oval(
                self._cx - r, self._cy - r,
                self._cx + r, self._cy + r,
                outline=color, width=2, fill="", tags="ripple",
            )
            self._item_ids.append(item_id)
        self._ripples = remaining
        if remaining:
            self._canvas.tag_lower("ripple")
            self._after_id = self._canvas.after(self._INTERVAL_MS, self._loop)
        else:
            self._running = False
