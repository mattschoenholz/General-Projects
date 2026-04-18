# bearclaw systemd user units

Live units installed to `~/.config/systemd/user/` on bearclaw (MSI Ubuntu 24.04, `matt` user).

This directory is the source of truth. To update: edit here, copy to the install path, then `systemctl --user daemon-reload`.

## Units

| File | Purpose |
|------|---------|
| `intel-vault-pull.service` | Oneshot: `git pull --ff-only` in `~/intel_vault/` |
| `intel-vault-pull.timer` | Fires the service 2 min after boot, then every 5 min |

## Install

```bash
cp intel-vault-pull.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now intel-vault-pull.timer
sudo loginctl enable-linger matt
```

## Check status

```bash
systemctl --user status intel-vault-pull.timer
systemctl --user list-timers intel-vault-pull.timer
journalctl --user -u intel-vault-pull.service -n 20
```
