# Pomodoro Web App Architecture Proposal

## 1. Overview

This document summarizes the agreed architecture for building a Pomodoro timer web application using Flask, HTML, CSS, and JavaScript.

Goals:
- Keep the first version simple and fast to deliver.
- Ensure the codebase is easy to unit test.
- Allow incremental evolution toward persistence, analytics, and richer UX.

## 2. High-Level Architecture

- Backend: Flask
  - Serves HTML templates and static assets.
  - Exposes JSON API endpoints for settings, sessions, and stats.
- Frontend: HTML/CSS/JavaScript (vanilla)
  - Renders UI and handles user interactions.
  - Runs timer behavior in the browser.
- Data Storage:
  - Phase 1: localStorage for lightweight preferences.
  - Phase 2: SQLite (via SQLAlchemy) for persistent settings/session history.

## 3. Project Structure

```text
1.pomodoro/
  app.py
  requirements.txt
  pomodoro/
    __init__.py
    config.py
    models.py
    routes/
      web.py                # HTML page routes
      api.py                # JSON API routes
    services/
      timer_stats.py        # stats and business orchestration
    core/
      domain/
        state_machine.py    # pure Pomodoro state transitions
        entities.py         # domain objects and value rules
        ports.py            # abstractions (clock/repository/scheduler)
    adapters/
      repositories/
        settings_repo.py
        sessions_repo.py
      time/
        system_clock.py
        scheduler.py
    templates/
      base.html
      index.html
    static/
      css/
        tokens.css
        app.css
      js/
        timer.js            # state machine integration + timer flow
        ui.js               # DOM bindings and rendering
        api.js              # fetch wrapper
```

## 4. Responsibilities by Layer

### 4.1 Core Domain (pure logic)
- Owns Pomodoro states and transitions.
- No Flask, no database, no DOM access.
- Input: current state + event.
- Output: next state + side-effect intents.

### 4.2 Services
- Coordinates use-cases (e.g., complete focus session, compute weekly stats).
- Applies domain rules (cycle counts, long break timing, validation rules).
- Depends on abstractions, not framework-specific code.

### 4.3 Adapters
- Repository adapters for SQLite/SQLAlchemy.
- Time/scheduler adapters for real runtime behavior.
- Can be swapped with test doubles.

### 4.4 Flask Routes
- Web routes: render templates.
- API routes: request validation, service invocation, response shaping.
- Keep route handlers thin.

### 4.5 Frontend
- `timer.js`: timer engine and state machine orchestration.
- `ui.js`: updates DOM from current state; no core timer rules.
- `api.js`: all HTTP concerns isolated.

## 5. API Endpoints (MVP)

- `GET /api/settings`
- `PUT /api/settings`
- `POST /api/sessions`
- `GET /api/stats?range=today|week|month`

Response and error format should be consistent and structured.

## 6. Data Model (initial)

### UserSettings
- `focus_minutes`
- `short_break_minutes`
- `long_break_minutes`
- `cycles_before_long_break`
- `auto_start_breaks`
- `auto_start_focus`
- `sound_enabled`

### PomodoroSession
- `started_at`
- `ended_at`
- `mode` (`focus`, `short_break`, `long_break`)
- `planned_seconds`
- `actual_seconds`
- `completed`

## 7. Testability-First Additions

### 7.1 Explicit State Machine
- Define all states/events explicitly.
- Maintain a transition table.
- Unit-test valid and invalid transitions.

### 7.2 Time Abstraction
- Use a `Clock` abstraction (`now()`) and scheduler abstraction.
- Inject fake time in tests to avoid waiting in real time.

### 7.3 Dependency Injection
- Routes depend on interfaces (`SettingsRepository`, `SessionRepository`, `StatsService`).
- Use in-memory or mock implementations for tests.

### 7.4 Strict Separation
- HTTP validation/formatting in routes.
- Business rules in domain/services.
- Persistence in repositories.

### 7.5 API Contract Validation
- Validate requests/responses with a schema library.
- Return structured errors (`code`, `message`, `details`).

## 8. Testing Strategy

- Unit tests (highest priority):
  - Domain state transitions
  - Cycle/long-break rules
  - Remaining-time calculations
- Integration tests:
  - Flask API + SQLite (test database)
- Frontend unit tests:
  - Timer logic and state reducers (without DOM)
- Lightweight E2E:
  - Start focus -> complete -> break transition
  - Pause/resume behavior

## 9. Delivery Plan

1. Build UI shell from mock (responsive HTML/CSS).
2. Implement client-side timer with state machine.
3. Add Flask API and SQLite persistence.
4. Add stats views and session history.
5. Polish UX (notifications, sounds, animations).

## 10. Non-Functional Notes

- Keep modules small and dependency direction one-way (outer layers depend on inner abstractions).
- Prefer deterministic logic for fast, stable tests.
- Log key backend events for diagnostics.
- Keep API backward-compatible as features are added.
