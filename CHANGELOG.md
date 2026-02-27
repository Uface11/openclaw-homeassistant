# Changelog

## 0.1.1 - 2026-02-27

### Added
- Config Flow connection/auth validation before entry creation.
- Re-auth flow for token renewal (`reauth_confirm`).
- Options Flow for runtime tuning:
  - `scan_interval`
  - `agent_id`
- Improved translation strings for setup and re-auth errors.
- Sensor device grouping via `OpenClaw Gateway` device info.
- `health_check` service documented and verified.

### Changed
- API client now uses structured error classes (auth/connection/http).
- Chat requests now target explicit agent model (`openclaw:<agent_id>`).
- Improved coordinator error messages and setup readiness handling.
- Polling interval now configurable from integration options.
- Manifest version bumped to `0.1.1`.

### Fixed
- Removed hardcoded routing behavior that could cause misrouted sessions.
- More robust HTTP error handling for Gateway responses.
- Improved availability behavior for sensor entities.

### Notes
- This release is focused on reliability and operational UX for daily use.
- OpenClaw integration verified live in Dockerized Home Assistant environment.
