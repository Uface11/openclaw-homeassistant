# OpenClaw Home Assistant (HACS)

OpenClaw integration for Home Assistant with a simple dashboard workflow:
- configure Gateway URL + API token
- send prompts/tasks to OpenClaw
- view status in Home Assistant

## MVP (v0.1)
- Config Flow (UI setup)
- Services: `openclaw.send_message`, `openclaw.run_task`, `openclaw.refresh_status`
- Sensor: online/offline + last response timestamp

## Install (HACS custom repository)
1. HACS → Integrations → Custom repositories
2. Add this repo URL, category: **Integration**
3. Install **OpenClaw**
4. Restart Home Assistant
5. Add integration via Settings → Devices & Services

## Development
Place integration files under:
`custom_components/openclaw/`

## Notes
This is HACS-first and intentionally scoped for a fast, stable MVP.
