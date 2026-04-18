# bearclaw Cloudflare Tunnel

Cloudflare Tunnel configuration exposing bearclaw's MCP server to the public internet.

## Tunnel

- **Name:** `bearclaw-mcp`
- **UUID:** `bc03d93c-e295-497e-8cee-4a97d40a95b1`
- **Public hostname:** `https://bearclaw.themakerbear.com`
- **Routes to:** `http://localhost:8765` (the FastMCP server)

## Credentials

The tunnel credentials JSON (`bc03d93c-e295-497e-8cee-4a97d40a95b1.json`) and the origin cert (`cert.pem`) live at `~/.cloudflared/` on bearclaw only. They are NOT committed to this repo — see `.gitignore`.

## Systemd service

Installed as a system service via `cloudflared service install`. Runs as root, reads config from `/etc/cloudflared/config.yml` (symlinked or copied from this file during install).

```bash
sudo systemctl status cloudflared
sudo systemctl restart cloudflared
sudo systemctl stop cloudflared   # use this if MCP server is unauthenticated and needs to be taken offline
```

## Security note

At Phase 2, `https://bearclaw.themakerbear.com/mcp` is publicly reachable with NO authentication. Phase 3 (GitHub OAuth) locks it down. Until Phase 3 is complete, stop the tunnel if you need to take the endpoint offline.
