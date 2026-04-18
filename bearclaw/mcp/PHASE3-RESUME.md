# Phase 3 Resume — GitHub OAuth

## Where we left off

Phase 2 (Cloudflare Tunnel) is complete and intentionally offline.

- Tunnel `bearclaw-mcp` exists and is configured
- `bearclaw.themakerbear.com` CNAME is live in Cloudflare DNS
- cloudflared systemd service is **stopped and disabled** (endpoint is dark)
- MCP server (`~/bearclaw-mcp/server.py`) is NOT running

## To bring the tunnel back up before Phase 3

```bash
sudo systemctl enable --now cloudflared
cd ~/bearclaw-mcp && source .venv/bin/activate && nohup python server.py > /tmp/bearclaw-mcp.log 2>&1 &
```

Verify locally first: `curl -s http://127.0.0.1:8765/mcp`
Verify externally: `curl -I https://bearclaw.themakerbear.com/mcp` (expect 405)

## What Phase 3 needs to do

### 3a — Create GitHub OAuth App

In GitHub: Settings → Developer settings → OAuth Apps → New OAuth App

- Application name: `bearclaw-mcp`
- Homepage URL: `https://bearclaw.themakerbear.com`
- Authorization callback URL: `https://claude.ai/api/mcp/auth_callback`

Copy the **Client ID** and generate a **Client Secret** (shown once — save it).

### 3b — Add OAuth to server.py

The spec references `fastmcp.server.auth.GitHubOAuthProvider` — verify this API
exists in FastMCP 3.2.4 before writing code. If it doesn't exist or the API has
changed, follow the MCP Python SDK reference implementation at:
`github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-auth`

Pattern (verify against actual FastMCP 3.2.4 API first):

```python
from fastmcp.server.auth import GitHubOAuthProvider
import os

mcp = FastMCP(
    name="bearclaw",
    auth=GitHubOAuthProvider(
        client_id=os.environ["GITHUB_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GITHUB_OAUTH_CLIENT_SECRET"],
        allowed_github_logins=["mattschoenholz"],
    ),
)
```

### 3c — Credentials file

Create `/home/matt/bearclaw-mcp/.env` (chmod 600):

```
GITHUB_OAUTH_CLIENT_ID=<from GitHub>
GITHUB_OAUTH_CLIENT_SECRET=<from GitHub>
```

### 3d — Systemd service for the MCP server itself

Write `/etc/systemd/system/bearclaw-mcp.service`:

```ini
[Unit]
Description=bearclaw MCP server
After=network.target

[Service]
User=matt
WorkingDirectory=/home/matt/bearclaw-mcp
EnvironmentFile=/home/matt/bearclaw-mcp/.env
ExecStart=/home/matt/bearclaw-mcp/.venv/bin/python server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3e — Verify OAuth discovery endpoint

```bash
curl https://bearclaw.themakerbear.com/.well-known/oauth-authorization-server
# Should return JSON with authorization_endpoint, token_endpoint, etc.
```

### 3f — Add to Claude.ai

Settings → Connectors → Add custom connector:
- Name: `bearclaw`
- Remote MCP server URL: `https://bearclaw.themakerbear.com/mcp`
- Advanced settings: paste GitHub OAuth Client ID and Client Secret

## Key facts

| Item | Value |
|------|-------|
| Tunnel UUID | `bc03d93c-e295-497e-8cee-4a97d40a95b1` |
| Credentials JSON | `~/.cloudflared/bc03d93c-e295-497e-8cee-4a97d40a95b1.json` |
| Tunnel config | `~/.cloudflared/config.yml` |
| MCP server | `~/bearclaw-mcp/server.py` |
| Venv | `~/bearclaw-mcp/.venv/` |
| FastMCP version | 3.2.4 |
| Python | 3.12.3 |

## Security reminder

Do NOT bring cloudflared back up until server.py has OAuth in place — the endpoint
is unauthenticated and publicly reachable the moment the tunnel is live.
