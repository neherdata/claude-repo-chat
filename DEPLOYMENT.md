# Deployment Guide - Claude Repo Chat

## Overview

Browser-based tmux terminal access for workspace instances. Each host gets its own subdomain and tmux session.

## Architecture

```
Browser → Cloudflare Tunnel → FastAPI (WebSocket) → PTY → tmux attach
```

## Deployment Targets

| Host | Subdomain | Port | Tmux Session |
|------|-----------|------|--------------|
| westoverxyz | workspace-westoverxyz.westover.services | 8091 | claude-session |
| westoverdev | workspace-westoverdev.westover.services | 8092 | claude-session |
| bumblebee (Mac) | workspace-bumblebee.westover.services | 8093 | claude-session |
| optimus-prime (Mac) | workspace-optimus.westover.services | 8094 | claude-session |

## Prerequisites

### Environment Variables
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export SECRET_KEY="random-secret-key-64-chars"
export CLOUDFLARE_AUD="your-cloudflare-aud"
```

### Tmux Session
Each host must have a tmux session running:
```bash
# Create tmux session named "claude-session"
tmux new-session -d -s claude-session

# Or attach to existing session
tmux attach-session -t claude-session
```

## Deployment

### Deploy to Specific Host
```bash
cd /home/westover/workspace/nds_server/ansible

# Deploy to westoverxyz
ansible-playbook playbooks/deploy-workspace-terminal.yml \
  -e target_host=westoverxyz

# Deploy to westoverdev
ansible-playbook playbooks/deploy-workspace-terminal.yml \
  -e target_host=westoverdev

# Deploy to Mac (requires SSH access configured)
ansible-playbook playbooks/deploy-workspace-terminal.yml \
  -e target_host=bumblebee
```

### Deploy to All Hosts
```bash
ansible-playbook playbooks/deploy-workspace-terminal.yml
```

## Cloudflare Tunnel Configuration

### Linux (systemd)
Tunnels configured automatically via Ansible. Service runs as:
```bash
sudo systemctl status cloudflared-workspace
```

### macOS (launchd)
Tunnel configuration at `~/.cloudflared/config.yml`:
```yaml
tunnel: <TUNNEL_ID>
credentials-file: ~/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: workspace-bumblebee.westover.services
    service: http://localhost:8093
  - service: http_status:404
```

Start tunnel:
```bash
launchctl load ~/Library/LaunchAgents/com.cloudflare.cloudflared.plist
```

## Service Management

### Linux
```bash
# Check status
sudo systemctl status claude-repo-chat-workspace

# View logs
sudo journalctl -u claude-repo-chat-workspace -f

# Restart
sudo systemctl restart claude-repo-chat-workspace
```

### macOS
```bash
# Check status
launchctl list | grep claude-repo-chat

# View logs
tail -f ~/Library/Logs/claude-repo-chat-workspace.log

# Restart
launchctl stop com.neherdata.claude-repo-chat-workspace
launchctl start com.neherdata.claude-repo-chat-workspace
```

## Testing

### Local Test (No Tunnel)
```bash
# Access directly via port
curl http://localhost:8091/health

# Open in browser
open http://localhost:8091
```

### Production Test (Via Tunnel)
```bash
# Health check
curl https://workspace-westoverxyz.westover.services/health

# Open in browser
open https://workspace-westoverxyz.westover.services
```

## Troubleshooting

### Terminal Not Connecting
1. Check tmux session exists:
   ```bash
   tmux list-sessions
   ```

2. Check service is running:
   ```bash
   # Linux
   sudo systemctl status claude-repo-chat-workspace

   # macOS
   launchctl list | grep claude-repo-chat
   ```

3. Check WebSocket connection:
   ```bash
   # In browser console
   # Look for WebSocket connection errors
   ```

### PTY Errors
```bash
# Check terminal permissions
ls -la /dev/ptmx

# Check service user permissions
id westover  # Linux
id $(whoami)  # macOS
```

### Cloudflare Tunnel Issues
```bash
# Linux
sudo systemctl status cloudflared-workspace
sudo journalctl -u cloudflared-workspace -f

# macOS
launchctl list | grep cloudflared
tail -f ~/.cloudflared/*.log
```

## Configuration

### Custom Tmux Session
Edit playbook variables:
```yaml
tmux_session_map:
  westoverxyz: "my-custom-session"
```

### Custom Port
Edit playbook variables:
```yaml
port_map:
  westoverxyz: 9000
```

### Disable Terminal Access
Set in playbook:
```yaml
enable_terminal: false
```

## Security

### Cloudflare Access
Configure email-based authentication:
1. Go to Cloudflare Zero Trust dashboard
2. Create Access Policy for `*.westover.services`
3. Require email verification
4. Add allowed email addresses

### Terminal Restrictions
- PTY runs as service user (westover or current user)
- No privilege escalation without sudo password
- tmux session isolation per user
- WebSocket authenticated via Cloudflare Access

## Monitoring

### Health Checks
All instances expose `/health` endpoint:
```bash
curl https://workspace-westoverxyz.westover.services/health
```

### Logs
Structured JSON logs via systemd/launchd:
```bash
# Linux
sudo journalctl -u claude-repo-chat-workspace -f --output=json

# macOS
tail -f ~/Library/Logs/claude-repo-chat-workspace.log
```

## Updating

### Update Application
```bash
# Pull latest code
cd /home/westover/workspace/claude-repo-chat
git pull

# Re-run deployment
cd /home/westover/workspace/nds_server/ansible
ansible-playbook playbooks/deploy-workspace-terminal.yml \
  -e target_host=westoverxyz
```

### Update Dependencies
Backend dependencies managed by PDM:
```bash
# In application directory
pdm sync --prod --clean
```

Service automatically restarts on deployment.
