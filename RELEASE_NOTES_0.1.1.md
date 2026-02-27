# OpenClaw Home Assistant v0.1.1

## Highlights
- Safer setup: credentials are validated before save.
- Better resilience: explicit auth/connection/http error handling.
- Better operations: options to change poll interval and agent ID without re-adding the integration.
- Re-auth support for expired/rotated tokens.
- Improved sensor behavior and device grouping.

## Upgrade Notes
1. Update custom component files in `custom_components/openclaw`.
2. Restart Home Assistant.
3. Open Integration Options and set desired:
   - Update interval
   - Agent ID
4. If token changed, run re-auth flow.

## Verification Checklist
- `openclaw.health_check` service returns success.
- `sensor.openclaw_gateway_status` becomes `online`.
- Active sessions / usage / uptime sensors are present.

## Known Environment Notes
- If Home Assistant is containerized, verify Gateway URL reachability from inside container.
- If GitHub access fails in HACS, validate container DNS/network path separately.
