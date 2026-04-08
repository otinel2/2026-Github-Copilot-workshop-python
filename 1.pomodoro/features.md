# Pomodoro Web App - Feature List

## 1. Core Timer Features (MVP)

- Start a focus session.
- Pause and resume an active timer.
- Reset current timer.
- Skip current phase (focus/break).
- Automatically transition between phases:
  - focus -> short break
  - focus -> long break after configured cycle count
  - break -> focus
- Show current phase label (Focus, Short Break, Long Break).
- Show remaining time with second-level updates.
- Ensure timer accuracy using target timestamp calculation (not naive interval-only counting).

## 2. User Settings

- Configure focus duration (minutes).
- Configure short break duration (minutes).
- Configure long break duration (minutes).
- Configure number of focus cycles before long break.
- Toggle auto-start breaks.
- Toggle auto-start focus sessions.
- Toggle sound notifications.
- Persist settings (Phase 1: localStorage, Phase 2: backend persistence).

## 3. Session Tracking and Statistics

- Save completed sessions via API.
- Record session metadata:
  - start time
  - end time
  - mode
  - planned seconds
  - actual seconds
  - completed flag
- Show daily focus summary.
- Show weekly focus summary.
- Show monthly focus summary.

## 4. Frontend UX and UI

- Responsive layout for desktop and mobile.
- Visual timer progress indicator (ring or bar).
- Clear controls for start/pause/reset/skip.
- Phase transition feedback (visual state change).
- Optional notification sound at phase completion.
- Basic accessibility support:
  - keyboard-focusable controls
  - adequate text contrast
  - semantic labels

## 5. Backend API Features

- GET /api/settings
- PUT /api/settings
- POST /api/sessions
- GET /api/stats?range=today|week|month
- Input validation for all request payloads.
- Consistent JSON error response format:
  - code
  - message
  - details

## 6. Architecture and Code Quality Features

- Keep domain state machine logic pure and framework-independent.
- Separate layers:
  - routes (HTTP)
  - services (business rules)
  - repositories (data access)
  - adapters (time/scheduler integration)
- Dependency injection for repositories/services.
- Clock abstraction for deterministic timer logic.

## 7. Testing Features

- Unit tests for state machine transitions.
- Unit tests for cycle and long-break rules.
- Unit tests for remaining-time calculations with fake clock.
- Integration tests for Flask API endpoints.
- Integration tests for persistence behavior with test database.
- Frontend unit tests for timer logic without DOM dependency.
- Lightweight end-to-end scenario tests for critical flows.

## 8. Delivery Milestones

1. Build static UI from mock.
2. Implement client-side timer engine.
3. Add Flask API and persistence.
4. Implement session stats views.
5. Add UX polish (notifications, animations) and stabilize tests.
