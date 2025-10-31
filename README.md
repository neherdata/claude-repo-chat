# Claude Repo Chat

Browser-based Claude interface for secure repository access with git-crypt support.

## Overview

Claude Repo Chat provides a web-based chat interface to interact with Claude on any git repository, with built-in support for git-crypt encrypted content. Designed for both technical and non-technical users to securely access and work with private repository data.

## Features

- 🤖 **Claude Chat Interface** - Natural language interaction with repository content
- 🔐 **git-crypt Support** - Transparent encryption/decryption of sensitive files
- 🌐 **Browser-based** - No local git/terminal knowledge required
- 📁 **Artifact Generation** - Create and download files (with automatic decryption)
- 🔒 **Cloudflare Access** - Email-based authentication and authorization
- 💾 **Context Persistence** - Shared knowledge across sessions and machines
- 💻 **Terminal Emulation** - Optional browser-based terminal for advanced users

## Use Cases

### Attorney Document Access
Secure access to encrypted legal documents, chat logs, and email records without requiring git expertise.

### Multi-Machine Workspace
Consistent Claude context across development machines (westoverdev, westoverxyz, optimus-prime, bumblebee) with browser-based terminal access.

## Tech Stack

- **Frontend**: React + xterm.js (terminal emulation)
- **Backend**: FastAPI (Python)
- **Auth**: Cloudflare Access
- **Deployment**: Docker on westoverxyz
- **Knowledge**: TBD (Vector/Graph DB or MCP Memory)

## Deployment

Deployed on westover.services infrastructure:
- `robert.westover.services` - Attorney access instance
- `workspace.westover.services` - Personal workspace instance

## Documentation

- [PROJECT.md](PROJECT.md) - Detailed project overview and architecture
- [CLAUDE.md](CLAUDE.md) - AI assistant context and development notes

## Status

🚧 **In Development** - See [PROJECT.md](PROJECT.md) for roadmap and timeline.

## Security

- All repository operations happen server-side
- git-crypt keys stored securely (never transmitted to client)
- HTTPS-only communication
- Email-based authentication via Cloudflare Access
- Audit logging of all access

## License

Private - NDS Infrastructure Project
