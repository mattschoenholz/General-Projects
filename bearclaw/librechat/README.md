# LibreChat — bearclaw family deploy

Self-hosted LibreChat running on bearclaw, exposed over Tailscale. Gives Matt's son a Claude-powered chat interface backed by a cost-capped Anthropic API key. Multi-user, Sonnet-only for general access, Opus available to Matt via the `Claude-Admin` custom endpoint.

## Live config

- Working directory: `~/librechat/` on bearclaw
- URL: `http://bearclaw:3080` (Tailscale only — not public internet)
- Two accounts: `matt@makerbear` (admin) and son's account
- Anthropic API key scoped to LibreChat only, $40/month cap set in Anthropic Console

## Files tracked here

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Upstream LibreChat compose — do not edit directly; use override |
| `docker-compose.override.yaml` | Mounts `librechat.yaml` into the api container |
| `librechat.yaml` | Model restrictions: Sonnet for all, Opus via Claude-Admin endpoint |
| `.env.example` | Placeholder config — copy to `.env` and fill in secrets |
| `.gitignore` | Ensures `.env` (with real secrets) is never committed |

## First-time setup

```bash
cd ~/librechat
# Secrets are already generated in .env — see .env.example for generation commands
docker compose up -d
docker compose logs -f api
```

## Updating LibreChat

```bash
cd ~/librechat
docker compose pull
docker compose up -d
# Check release notes at https://github.com/danny-avila/LibreChat/releases first
```

## Monitoring

- Anthropic usage: `https://console.anthropic.com/usage`
- LibreChat admin panel: `http://bearclaw:3080/admin` (log in as matt@makerbear)
- Logs: `docker compose logs -f api`
- Mongo data: `~/librechat/data-node/` — back up weekly

## Cost projection

~$10–30/month for casual teen usage at Sonnet rates. $40/month hard cap at Anthropic Console.
See full spec: `~/intel_vault/00_System/Chat Intake/2026-04-18-librechat-family-spec.md`
