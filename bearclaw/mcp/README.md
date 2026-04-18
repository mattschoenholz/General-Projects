# bearclaw MCP Server

A FastMCP server that exposes the intel_vault to Claude.ai as a custom MCP connector.

## Phase Status

- **Phase 0** — Prerequisites: done (Python 3.12.3, FastMCP 3.2.4)
- **Phase 1** — Barebones vault read tools, local only: done
- **Phase 2** — Cloudflare Tunnel (bearclaw.themakerbear.com): done — publicly reachable, NO auth yet
- **Phase 3** — GitHub OAuth authentication: not yet implemented

## Tools (Phase 1)

| Tool | Description |
|------|-------------|
| `vault_read(path)` | Read a file from intel_vault. Path relative to vault root. |
| `vault_list(folder)` | List markdown files in a vault folder. Empty string = vault root. |
| `vault_search(query, folder)` | Grep-style search across vault markdown. Returns up to 50 matches. |

All tools enforce path containment — requests that escape `/home/matt/intel_vault/` return an error.

## Running locally

```bash
cd ~/bearclaw-mcp
source .venv/bin/activate
python server.py
# Listens on http://127.0.0.1:8765/mcp
```

## Transport

Streamable HTTP on `127.0.0.1:8765`, exposed publicly via Cloudflare Tunnel at `https://bearclaw.themakerbear.com/mcp`.

## Architecture

See `~/intel_vault/00_System/Chat Intake/2026-04-18-mcp-server-spec.md` for the full design rationale, security decisions, and phased build plan.
