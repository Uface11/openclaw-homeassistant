# OpenClaw Home Assistant (HACS)

OpenClaw integration for Home Assistant with a simple dashboard workflow:
- configure Gateway URL + API token
- send prompts/tasks to OpenClaw
- view status in Home Assistant

## MVP (v0.1)
- Config Flow (UI setup: Gateway URL, API token, agent id)
- Services: `openclaw.send_message`, `openclaw.run_task`, `openclaw.refresh_status`
- Sensor: online/offline + status payload

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

## Dashboard Card (Step 2)
A first board-style card is included at:
`www/openclaw-board-card.js`

Add as Lovelace resource:
- URL: `/local/openclaw-board-card.js`
- Type: `module`

Example card config:
```yaml
type: custom:openclaw-board-card
title: OpenClaw Board
icon: mdi:robot-outline
board_url: https://github.com/AlexPEClub/openclaw_react_board
quick_actions:
  - Status check
  - Create Kanban task
  - Summarize updates
```

## Development
- Integration backend: `custom_components/openclaw/`
- Frontend card: `www/openclaw-board-card.js`

## Notes
This is HACS-first and intentionally scoped for a fast, stable MVP.
