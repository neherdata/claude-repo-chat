# Claude Repo Chat - Project Overview

## Vision

Browser-based Claude interface that enables secure, authenticated access to git repositories with built-in support for git-crypt encrypted content. Provides both chat-based interaction and terminal emulation for repository operations.

## Core Objectives

### 1. Knowledge Service (Context Persistence)
- Shared context across all Claude instances (automation runners + interactive sessions)
- Persistent knowledge graph for cross-session continuity
- Context available on:
  - westoverdev (GitHub Actions runner host)
  - westoverxyz (app server)
  - optimus-prime (MacBook Pro)
  - bumblebee (MacBook Air)

### 2. Repository Chat Interface
- Point the webapp at any repository
- Claude chat interface with full repo context
- Support for git-crypt encrypted repositories
- Automated encryption/decryption handling
- Downloadable artifacts (auto-decrypted if needed)
- Commits generated artifacts back to repo

### 3. Secure Access Control
- Cloudflare Access for authentication
- Email-based verification
- Per-user, per-repository access control
- Secure handling of encrypted content

## Initial Use Cases

### Use Case 1: Attorney Access (Robert Cummings)
**Problem**: Non-technical attorney needs secure access to private chat/email records stored in git-crypt encrypted repository

**Solution**:
- Deploy at `robert.westover.services` (or similar subdomain)
- Cloudflare Access with robert@[domain].com authentication
- Chat interface to query encrypted documents
- Generate reports/summaries as downloadable PDFs
- Claude handles encryption/decryption transparently

**Requirements**:
- Simple, intuitive web interface
- No git/command-line knowledge required
- Secure access to encrypted content
- Audit trail of access and queries

### Use Case 2: Personal Workspace Access
**Problem**: Need consistent Claude access across multiple development machines with shared context

**Solution**:
- Deploy at `workspace.westover.services`
- Terminal emulation in browser for tmux sessions
- Access workspaces on:
  - westoverdev (GitHub runner)
  - westoverxyz (app server)
  - optimus-prime (Mac)
  - bumblebee (Mac)
- Shared knowledge service for context continuity

**Requirements**:
- Browser-based terminal emulation
- Secure authentication (personal use)
- Context persistence across machines
- Support for encrypted repository operations

## Technical Architecture

### Frontend
- **Technology**: React (web) + Terminal emulation (xterm.js or similar)
- **Features**:
  - Chat interface for Claude interaction
  - File browser for repository navigation
  - Terminal emulator for direct git/shell access
  - Artifact preview/download
  - Encryption status indicators

### Backend
- **Technology**: FastAPI (Python)
- **Components**:
  - Claude API integration
  - Git operations (clone, commit, push)
  - git-crypt encryption/decryption
  - File system management
  - WebSocket for real-time chat
  - Terminal session management (pty)

### Knowledge Service
- **Technology**: TBD (Vector DB? Graph DB? MCP Memory?)
- **Features**:
  - Persistent context storage
  - Cross-session knowledge sharing
  - User-specific and global contexts
  - Repository-specific knowledge

### Deployment
- **Platform**: westover.services (Cloudflare-fronted)
- **Infrastructure**: westoverxyz (app server)
- **Auth**: Cloudflare Access
- **Subdomains**:
  - `robert.westover.services` - Attorney access instance
  - `workspace.westover.services` - Personal workspace instance
  - Landing page link from main westover.services

## Security Considerations

1. **Encrypted Repository Access**:
   - git-crypt keys must be securely managed
   - Decryption only happens server-side
   - No plaintext transmission of sensitive data
   - Keys stored in secure location (secrets management)

2. **Authentication**:
   - Cloudflare Access email verification
   - Per-repository access control
   - Session management and timeout
   - Audit logging of access

3. **Artifact Handling**:
   - Generated files maintain encryption status
   - Downloads are secure (HTTPS only)
   - Temporary files cleaned up
   - Encryption state tracked in metadata

## Open Questions

1. **Knowledge Service Implementation**:
   - What technology for persistent context? (Vector DB, Graph DB, MCP Memory extension?)
   - How to sync context across machines?
   - Storage location and backup strategy?

2. **Repository Naming**:
   - What to call this service? Options:
     - claude-repo-chat (current name)
     - secure-repo-assistant
     - repo-workspace
     - claude-workspace

3. **Terminal Emulation**:
   - Full terminal emulator vs limited shell?
   - tmux integration for personal workspace?
   - Security boundaries for shell access?

4. **Multi-tenancy**:
   - Single deployment with per-user instances?
   - Separate deployments per use case?
   - Resource isolation strategy?

5. **Git-crypt Key Management**:
   - How are keys provisioned per user/repo?
   - Key rotation strategy?
   - Backup and recovery?

6. **Artifact Management**:
   - Storage limits for generated artifacts?
   - Retention policy?
   - Automatic cleanup?

## Next Steps

1. Define knowledge service architecture and technology
2. Choose terminal emulation approach
3. Design authentication and authorization flow
4. Plan git-crypt key management
5. Create initial prototype with basic chat interface
6. Deploy first instance for attorney use case
7. Extend to personal workspace use case

## Timeline

**Phase 1: Foundation (Week 1-2)**
- Basic FastAPI backend
- React chat frontend
- Claude API integration
- Simple repository cloning

**Phase 2: Encryption Support (Week 3)**
- git-crypt integration
- Encryption/decryption handling
- Secure artifact downloads

**Phase 3: Knowledge Service (Week 4)**
- Context persistence implementation
- Cross-session knowledge sharing
- Repository-specific context

**Phase 4: Terminal Emulation (Week 5-6)**
- Browser terminal integration
- tmux session management
- Secure shell access

**Phase 5: Production Deploy (Week 7)**
- Cloudflare Access setup
- Deploy attorney instance
- Testing and refinement

**Phase 6: Workspace Extension (Week 8)**
- Multi-machine workspace access
- Terminal emulation for personal use
- Full integration testing
