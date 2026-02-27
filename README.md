# OpenClaw Home Assistant (HACS)

OpenClaw integration for Home Assistant with a simple dashboard workflow:
- configure Gateway URL + API token
- send prompts/tasks to OpenClaw
- view status in Home Assistant

## Release (v0.1.1)
- Validated Config Flow (checks connectivity/auth before saving)
- Re-auth flow for expired/invalid token
- Options Flow (change poll interval + agent id without re-adding)
- Services: `openclaw.send_message`, `openclaw.run_task`, `openclaw.refresh_status`, `openclaw.health_check`
- Sensor suite with device grouping + availability handling

## Gateway endpoints used
- `POST /tools/invoke` for status (`session_status` tool)
- `POST /v1/chat/completions` for prompt/task execution

Required gateway setting for chat:
```json
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": { "enabled": true }
      }
    }
  }
}
```

## Install (HACS custom repository)
1. HACS → Integrations → Custom repositories
2. Add this repo URL, category: **Integration**
3. Install **OpenClaw**
4. Restart Home Assistant
5. Add integration via Settings → Devices & Services

## Dashboard Card (v2)
Board-style card inspired by `openclaw_react_board` is included at:
`www/openclaw-board-card.js`

Features (v2):
- 4 Kanban columns: Offen / In Arbeit / Review / Erledigt
- Drag & drop cards between columns
- Add task inline per column (Enter)
- Delete task button
- Local persistence via browser `localStorage`
- Optional sync actions to OpenClaw (`run_task`) on add/move
- Top-right actions: **Update** + **Health**

## Exposed server entities (Top 5)
- `sensor.openclaw_gateway_status`
- `sensor.openclaw_gateway_active_sessions`
- `sensor.openclaw_gateway_usage_tokens`
- `sensor.openclaw_gateway_cost_estimate`
- `sensor.openclaw_gateway_uptime_seconds`

Add as Lovelace resource:
- URL: `/local/openclaw-board-card.js`
- Type: `module`

Example card config:
```yaml
type: custom:openclaw-board-card
title: OpenClaw Board
icon: mdi:robot-outline
board_url: https://github.com/AlexPEClub/openclaw_react_board
storage_key: openclaw_board_v2
sync_with_openclaw: true
```

## Development
- Integration backend: `custom_components/openclaw/`
- Frontend card: `www/openclaw-board-card.js`

## Notes
This is HACS-first and intentionally scoped for a fast, stable MVP.
