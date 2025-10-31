# Claude Repo Chat - AI Development Context

## Project Purpose

This is a **browser-based Claude interface** that enables secure, authenticated access to git repositories with built-in git-crypt support. Think of it as "Claude-as-a-Service" for specific repositories with encrypted content.

## Architecture Overview

```
User Browser → Cloudflare Access → FastAPI Backend → Claude API
                                         ↓
                                    Git Operations
                                         ↓
                                  git-crypt decrypt
                                         ↓
                                 Knowledge Service
```

## Key Components

### 1. Frontend (React)
**Location**: `frontend/`

- Chat interface for Claude interaction
- File browser for repository navigation
- Terminal emulator (xterm.js) for advanced users
- Artifact preview and download
- Encryption status indicators

### 2. Backend (FastAPI)
**Location**: `backend/`

**Core Functions**:
- Claude API integration (streaming chat)
- Git repository operations (clone, commit, push)
- git-crypt encryption/decryption
- File system management (temp workspace per session)
- WebSocket for real-time chat
- PTY for terminal sessions

**Endpoints** (planned):
- `POST /chat` - Send message to Claude
- `GET /ws/chat` - WebSocket for streaming responses
- `GET /repos/{repo_id}` - Repository info
- `POST /repos/{repo_id}/clone` - Clone repository
- `GET /repos/{repo_id}/files` - List files
- `GET /repos/{repo_id}/files/{path}` - Get file content
- `POST /artifacts` - Generate artifact
- `GET /artifacts/{id}/download` - Download artifact
- `GET /ws/terminal` - WebSocket terminal session

### 3. Knowledge Service
**Location**: TBD

**Requirements**:
- Persistent context storage across sessions
- Repository-specific knowledge graphs
- User-specific contexts
- Cross-machine synchronization
- Integration with Claude API

**Technology Options**:
1. **MCP Memory** - Anthropic's Model Context Protocol memory server
2. **Vector DB** - Pinecone, Weaviate, or Qdrant
3. **Graph DB** - Neo4j for relationship tracking
4. **Hybrid** - Vector search + graph relationships

### 4. Authentication (Cloudflare Access)
**Location**: Cloudflare dashboard configuration

- Email-based authentication
- Per-subdomain access rules
- JWT validation in backend
- Session management

## Development Workflow

### Prerequisites
- Python 3.13+ (via pyenv on westoverxyz)
- PDM for Python dependency management
- Node.js 20+ for frontend
- Docker for deployment
- git-crypt for encryption support

### Local Development
```bash
# Backend
cd backend
pdm install
pdm run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### Docker Deployment
```bash
docker-compose up -d
```

### Ansible Deployment
```bash
ansible-playbook -i ../nds_server/ansible/inventory/hosts.yml ansible/deploy.yml
```

## Security Considerations

### git-crypt Key Management
1. Keys stored in `/opt/claude-repo-chat/keys/{repo_id}.key`
2. Keys provisioned via Ansible from nds_server/secrets/
3. Keys never leave server, never transmitted to client
4. Each repository gets isolated workspace: `/tmp/repos/{session_id}/{repo_name}/`

### Session Isolation
- Each user session gets unique workspace
- Workspaces cleaned up after session end (or timeout)
- No cross-session data leakage
- Separate git-crypt unlock per workspace

### Audit Logging
- All repository access logged
- All Claude queries logged
- All artifact downloads logged
- Logs stored in journald (systemd)

## Integration with NDS Infrastructure

### Deployment Target
- **Server**: westoverxyz (100.86.176.6 via Tailscale)
- **User**: westover
- **Service**: systemd service `claude-repo-chat.service`
- **Port**: TBD (check nds_server port allocation)

### Cloudflare Integration
- **Tunnels**: Similar to ghost-hunter-api and nsfw_detect_api
- **Subdomains**:
  - `robert.westover.services` → westoverxyz:PORT
  - `workspace.westover.services` → westoverxyz:PORT
- **Access Rules**: Email-based per subdomain

### Secrets Management
- Claude API key stored in nds_server/secrets/
- git-crypt keys stored in nds_server/secrets/
- Deployed via Ansible
- Environment variables in systemd service

## Initial Use Case: Attorney Access (Robert Cummings)

### Repository
- Private repo with chat logs and email records
- git-crypt encrypted
- Robert needs read-only query access

### User Flow
1. Navigate to `robert.westover.services`
2. Authenticate with email (robert@[domain].com)
3. Repository auto-loaded and decrypted
4. Chat with Claude about documents
5. Request summaries, analyses, or reports
6. Download artifacts (PDFs, etc.)
7. Artifacts auto-committed to repo

### Claude Capabilities
- "Show me all emails from [person] in [date range]"
- "Summarize the conversation about [topic]"
- "Generate a timeline of events"
- "Create a report on [subject]"
- "What was discussed on [date]?"

## Future Use Case: Personal Workspace

### Multi-Machine Access
- Access tmux sessions on westoverdev, westoverxyz, optimus-prime, bumblebee
- Shared context across all machines
- Browser-based terminal emulation
- Repository operations with encryption support

### Terminal Integration
- xterm.js for terminal emulation
- PTY on backend (pty.spawn for shell)
- WebSocket for real-time terminal I/O
- tmux attach/detach support

## Development Guidelines

### Code Style
- **Python**: PEP 8, type hints, async/await for I/O
- **TypeScript**: ESLint + Prettier
- **Git**: Conventional commits (feat:, fix:, docs:, etc.)

### Testing
- **Backend**: pytest with async support
- **Frontend**: Jest + React Testing Library
- **E2E**: Playwright for full user flows

### Documentation
- Docstrings for all public functions
- OpenAPI schema for FastAPI endpoints
- Component documentation for React

## Known Challenges

1. **git-crypt Performance**: Decryption on large repos may be slow
2. **Session Management**: Need efficient cleanup of temp workspaces
3. **Terminal Security**: PTY access needs careful sandboxing
4. **Context Limits**: Claude API has token limits, need smart summarization
5. **Real-time Sync**: Knowledge service sync across machines

## Related Projects

- **nds_server**: Ansible playbooks and shared infrastructure config
- **ghost-hunter-api**: Similar FastAPI + Cloudflare Tunnel pattern
- **nsfw_detect_api**: Similar API architecture reference

## Commands to Remember

```bash
# Start development
pdm run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Run tests
pdm run pytest

# Build Docker image
docker build -t claude-repo-chat:latest .

# Deploy with Ansible
ansible-playbook -i ../nds_server/ansible/inventory/hosts.yml ansible/deploy.yml

# Check service status
ssh westoverxyz "sudo systemctl status claude-repo-chat"

# View logs
ssh westoverxyz "sudo journalctl -u claude-repo-chat -f"
```

## TODO

See PROJECT.md for full roadmap. Immediate tasks:

1. ✅ Create repository
2. ✅ Bootstrap project structure
3. ⏳ Define knowledge service architecture
4. ⏳ Create FastAPI backend skeleton
5. ⏳ Create React frontend skeleton
6. ⏳ Implement Claude API integration
7. ⏳ Implement git-crypt support
8. ⏳ Set up Cloudflare Access
9. ⏳ Deploy first instance for attorney

## Questions for User

(To be asked after bootstrap complete - see PROJECT.md Open Questions section)
